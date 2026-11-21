"""Creates a user or resets their password: python scripts/set_user.py <username>.
Prompts without echo (or reads stdin when piped), so the password never lands in shell history."""
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import connect, init_db  # noqa: E402
from app.security import hash_password  # noqa: E402


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/set_user.py <username>")
    username = sys.argv[1]
    if sys.stdin.isatty():
        password = getpass.getpass(f"Password for {username}: ")
    else:
        password = sys.stdin.readline().rstrip("\n")
    if not password:
        sys.exit("empty password")

    with connect() as conn:
        init_db(conn)
        conn.execute(
            """INSERT INTO users (username, password_hash) VALUES (%s, %s)
               ON CONFLICT (lower(username)) DO UPDATE SET password_hash = excluded.password_hash,
                 failed_attempts = 0, locked_until = NULL""",
            (username, hash_password(password)),
        )
    print(f'Saved user "{username}"')


if __name__ == "__main__":
    main()
