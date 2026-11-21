"""User lookups shared by the routers, starting with who the logged-in person chats with.
The app is built for exactly two users; with more, the lowest id other than yours wins."""
import sqlite3


def get_peer(db: sqlite3.Connection, user_id: int) -> sqlite3.Row | None:
    return db.execute("SELECT id, username FROM users WHERE id != ? ORDER BY id LIMIT 1",
                      (user_id,)).fetchone()
