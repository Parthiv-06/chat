"""User lookups shared by the routers, starting with who the logged-in person chats with.
The app is built for exactly two users; with more, the lowest id other than yours wins."""
from .db import Conn


def get_peer(db: Conn, user_id: int) -> dict | None:
    return db.execute("SELECT id, username FROM users WHERE id <> %s ORDER BY id LIMIT 1",
                      (user_id,)).fetchone()
