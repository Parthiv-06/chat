"""PostgreSQL connection pool and schema for the chat backend: users, login sessions, messages.
DATABASE_URL comes from the environment or backend/.env; every connection runs in autocommit."""
import os
from collections.abc import Iterator
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

Conn = psycopg.Connection[dict]

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id              bigint      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username        text        NOT NULL CHECK (char_length(username) BETWEEN 1 AND 64),
    password_hash   text        NOT NULL,
    failed_attempts integer     NOT NULL DEFAULT 0,
    locked_until    timestamptz,
    created_at      timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS users_username_lower ON users (lower(username));

CREATE TABLE IF NOT EXISTS sessions (
    token_hash  text        PRIMARY KEY,
    user_id     bigint      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at  timestamptz NOT NULL DEFAULT now(),
    expires_at  timestamptz NOT NULL
);
CREATE INDEX IF NOT EXISTS sessions_user_id ON sessions (user_id);

CREATE TABLE IF NOT EXISTS messages (
    id            bigint      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sender_id     bigint      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recipient_id  bigint      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    body          text        NOT NULL CHECK (char_length(body) BETWEEN 1 AND 4000),
    created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS messages_pair ON messages (sender_id, recipient_id, id);
"""

_pool: ConnectionPool | None = None


def database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set; copy backend/.env.example to backend/.env")
    return url


def connect() -> Conn:
    """A standalone connection for scripts; the web app uses the pool via get_db instead."""
    return psycopg.connect(database_url(), autocommit=True, row_factory=dict_row)


def init_db(conn: Conn) -> None:
    conn.execute(SCHEMA)


def open_pool() -> None:
    """Opens the shared pool and creates missing tables; fails fast if Postgres is unreachable."""
    global _pool
    _pool = ConnectionPool(database_url(), min_size=1, max_size=10, open=True,
                           kwargs={"autocommit": True, "row_factory": dict_row})
    _pool.wait(timeout=10)
    with _pool.connection() as conn:
        init_db(conn)


def close_pool() -> None:
    if _pool:
        _pool.close()


def get_db() -> Iterator[Conn]:
    """FastAPI dependency lending each request a pooled connection, returned afterwards."""
    with _pool.connection() as conn:
        yield conn
