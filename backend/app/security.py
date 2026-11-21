"""Password hashing (Argon2id), login checks with lockout, and cookie-backed server sessions.
Only SHA-256 of a session token is stored, so a leaked DB cannot be replayed as a login."""
import hashlib
import os
import secrets
import sqlite3
import time

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError
from fastapi import Cookie, Depends, HTTPException, Response, status

from .db import get_db

COOKIE_NAME = "sid"
MAX_FAILED = 5
LOCK_SECONDS = 15 * 60
SESSION_SECONDS = 7 * 24 * 60 * 60
SECURE_COOKIES = os.environ.get("ENV") == "production"

hasher = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)

# Verified against when the username is unknown, so response time does not reveal valid names.
_DUMMY_HASH = hasher.hash("not-a-real-password")


def _now() -> int:
    return int(time.time())


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def hash_password(password: str) -> str:
    return hasher.hash(password)


def _verify(stored_hash: str, password: str) -> bool:
    try:
        return hasher.verify(stored_hash, password)
    except (VerificationError, InvalidHashError):
        return False


class LoginError(Exception):
    """Raised by check_credentials; .locked tells a lockout apart from a wrong password."""

    def __init__(self, locked: bool = False):
        self.locked = locked


def check_credentials(db: sqlite3.Connection, username: str, password: str) -> sqlite3.Row:
    """Returns the user row, or raises LoginError.
    Counts failures per user and locks the account for 15 minutes after 5 in a row."""
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if user is None:
        _verify(_DUMMY_HASH, password)
        raise LoginError()
    if user["locked_until"] and user["locked_until"] > _now():
        raise LoginError(locked=True)

    if not _verify(user["password_hash"], password):
        failed = user["failed_attempts"] + 1
        lock_until = _now() + LOCK_SECONDS if failed >= MAX_FAILED else None
        db.execute(
            "UPDATE users SET failed_attempts = ?, locked_until = ? WHERE id = ?",
            (0 if lock_until else failed, lock_until, user["id"]),
        )
        raise LoginError(locked=lock_until is not None)

    db.execute("UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE id = ?",
               (user["id"],))
    if hasher.check_needs_rehash(user["password_hash"]):
        db.execute("UPDATE users SET password_hash = ? WHERE id = ?",
                   (hash_password(password), user["id"]))
    return user


def create_session(db: sqlite3.Connection, user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    db.execute("DELETE FROM sessions WHERE expires_at <= ?", (_now(),))
    db.execute("INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)",
               (_sha256(token), user_id, _now() + SESSION_SECONDS))
    return token


def destroy_session(db: sqlite3.Connection, token: str | None) -> None:
    if token:
        db.execute("DELETE FROM sessions WHERE token_hash = ?", (_sha256(token),))


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(COOKIE_NAME, token, max_age=SESSION_SECONDS, path="/",
                        httponly=True, samesite="strict", secure=SECURE_COOKIES)


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/", httponly=True, samesite="strict",
                           secure=SECURE_COOKIES)


def current_user(sid: str | None = Cookie(default=None),
                 db: sqlite3.Connection = Depends(get_db)) -> sqlite3.Row:
    """Dependency for protected routes: returns the logged-in user row (id, username).
    Answers 401 when the cookie is missing, unknown, or expired."""
    row = sid and db.execute(
        """SELECT u.id, u.username FROM sessions s JOIN users u ON u.id = s.user_id
           WHERE s.token_hash = ? AND s.expires_at > ?""",
        (_sha256(sid), _now()),
    ).fetchone()
    if not row:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not logged in")
    return row
