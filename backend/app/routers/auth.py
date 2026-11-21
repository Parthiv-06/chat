"""Login, logout, who-am-I and who-is-the-other-person endpoints under /api/auth.
Routes are plain def, so FastAPI runs the slow Argon2 checks in a thread, off the event loop."""
import sqlite3

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status

from .. import security
from ..db import get_db
from ..schemas import LoginRequest, UserResponse
from ..users import get_peer

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=UserResponse)
def login(body: LoginRequest, response: Response,
          sid: str | None = Cookie(default=None), db: sqlite3.Connection = Depends(get_db)):
    try:
        user = security.check_credentials(db, body.username.strip(), body.password)
    except security.LoginError as e:
        if e.locked:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS,
                                "Too many attempts. Try again in 15 minutes.")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid username or password")

    security.destroy_session(db, sid)
    security.set_session_cookie(response, security.create_session(db, user["id"]))
    return {"user": {"id": user["id"], "username": user["username"]}}


@router.post("/logout")
def logout(response: Response, sid: str | None = Cookie(default=None),
           db: sqlite3.Connection = Depends(get_db)):
    security.destroy_session(db, sid)
    security.clear_session_cookie(response)
    return {"ok": True}


@router.get("/me", response_model=UserResponse)
def me(user: sqlite3.Row = Depends(security.current_user)):
    return {"user": {"id": user["id"], "username": user["username"]}}


@router.get("/peer", response_model=UserResponse)
def peer(user: sqlite3.Row = Depends(security.current_user),
         db: sqlite3.Connection = Depends(get_db)):
    """The one other user, i.e. who the logged-in person chats with (see users.get_peer)."""
    row = get_peer(db, user["id"])
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No other user yet")
    return {"user": {"id": row["id"], "username": row["username"]}}
