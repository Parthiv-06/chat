"""Stores a profile picture in the database: python scripts/set_avatar.py <username> <image file>.
Accepts JPEG, PNG or WebP up to 2 MB; replaces any existing avatar for that user."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import connect, init_db  # noqa: E402

MAX_BYTES = 2 * 1024 * 1024
SIGNATURES = {b"\xff\xd8\xff": "image/jpeg", b"\x89PNG\r\n\x1a\n": "image/png"}


def content_type(data: bytes) -> str | None:
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return next((t for sig, t in SIGNATURES.items() if data.startswith(sig)), None)


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("usage: python scripts/set_avatar.py <username> <image file>")
    username, path = sys.argv[1], Path(sys.argv[2])
    data = path.read_bytes()
    kind = content_type(data)
    if not kind:
        sys.exit(f"{path} is not a JPEG, PNG or WebP image")
    if len(data) > MAX_BYTES:
        sys.exit(f"{path} is {len(data) // 1024} KB; the limit is 2 MB")

    with connect() as conn:
        init_db(conn)
        user = conn.execute("SELECT id FROM users WHERE lower(username) = lower(%s)",
                            (username,)).fetchone()
        if not user:
            sys.exit(f'No user "{username}"; create it first with scripts/set_user.py')
        conn.execute("""INSERT INTO avatars (user_id, image, content_type) VALUES (%s, %s, %s)
                        ON CONFLICT (user_id) DO UPDATE SET image = excluded.image,
                          content_type = excluded.content_type, updated_at = now()""",
                     (user["id"], data, kind))
    print(f'Saved avatar for "{username}" ({kind}, {len(data) // 1024} KB)')


if __name__ == "__main__":
    main()
