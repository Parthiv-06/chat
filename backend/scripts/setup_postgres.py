"""One-time Postgres setup: creates the app role and database from DATABASE_URL, the tables, and
copies users/sessions/messages from the old data/chat.db. Safe to re-run; existing rows are kept."""
import getpass
import os
import sqlite3
import sys
from pathlib import Path

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import connect, database_url, init_db  # noqa: E402

SQLITE_PATH = Path(__file__).resolve().parent.parent / "data" / "chat.db"


def admin_password() -> str:
    if "PGADMIN_PASSWORD" in os.environ:
        return os.environ["PGADMIN_PASSWORD"]
    if sys.stdin.isatty():
        return getpass.getpass("Password for the Postgres superuser 'postgres': ")
    return sys.stdin.readline().rstrip("\n")


def create_role_and_database(target: dict) -> None:
    """Connects as the superuser to create the app's login role and database if missing."""
    admin = psycopg.connect(host=target.get("host", "localhost"), port=target.get("port", 5432),
                            user=os.environ.get("PGADMIN_USER", "postgres"),
                            password=admin_password(), dbname="postgres", autocommit=True)
    with admin:
        role, db = target["user"], target["dbname"]
        if not admin.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (role,)).fetchone():
            admin.execute(sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                sql.Identifier(role), sql.Literal(target["password"])))
            print(f"Created role {role}")
        if not admin.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db,)).fetchone():
            admin.execute(sql.SQL("CREATE DATABASE {} OWNER {}").format(
                sql.Identifier(db), sql.Identifier(role)))
            print(f"Created database {db}")


def import_sqlite(pg) -> None:
    """Copies rows with their original ids, then moves the id counters past them."""
    if not SQLITE_PATH.exists():
        print("No data/chat.db to import")
        return
    src = sqlite3.connect(SQLITE_PATH)
    tables = {r[0] for r in src.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    with pg.transaction():
        for row in src.execute("SELECT id, username, password_hash, failed_attempts, "
                               "locked_until, created_at FROM users"):
            pg.execute("""INSERT INTO users OVERRIDING SYSTEM VALUE VALUES
                          (%s, %s, %s, %s, to_timestamp(%s), to_timestamp(%s))
                          ON CONFLICT DO NOTHING""", row)
        for row in src.execute("SELECT token_hash, user_id, created_at, expires_at FROM sessions"):
            pg.execute("""INSERT INTO sessions VALUES
                          (%s, %s, to_timestamp(%s), to_timestamp(%s)) ON CONFLICT DO NOTHING""",
                       row)
        if "messages" in tables:
            for row in src.execute("SELECT id, sender_id, recipient_id, body, created_at "
                                   "FROM messages"):
                pg.execute("""INSERT INTO messages OVERRIDING SYSTEM VALUE VALUES
                              (%s, %s, %s, %s, to_timestamp(%s / 1000.0))
                              ON CONFLICT DO NOTHING""", row)
        for table in ("users", "messages"):
            pg.execute(sql.SQL("SELECT setval(pg_get_serial_sequence({t}, 'id'), "
                               "COALESCE(MAX(id), 0) + 1, false) FROM {i}").format(
                t=sql.Literal(table), i=sql.Identifier(table)))
    counts = {t: pg.execute(sql.SQL("SELECT count(*) AS n FROM {}").format(sql.Identifier(t)))
              .fetchone()["n"] for t in ("users", "sessions", "messages")}
    print("Postgres now has", ", ".join(f"{n} {t}" for t, n in counts.items()))


def main() -> None:
    create_role_and_database(conninfo_to_dict(database_url()))
    with connect() as pg:
        init_db(pg)
        print("Tables ready")
        import_sqlite(pg)


if __name__ == "__main__":
    main()
