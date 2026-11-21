"""Profile pictures at /api/avatars/{user_id}, served only to a logged-in user (you or your peer).
Files are <username>.jpg in AVATAR_DIR (default backend/data/avatars), kept out of the public repo."""
import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from .. import security
from ..db import Conn, get_db
from ..users import get_peer

AVATAR_DIR = Path(os.environ.get(
    "AVATAR_DIR", Path(__file__).resolve().parent.parent.parent / "data" / "avatars")).resolve()

router = APIRouter(prefix="/api/avatars", tags=["avatars"])


@router.get("/{user_id}")
def avatar(user_id: int, user: dict = Depends(security.current_user), db: Conn = Depends(get_db)):
    """JPEG for you or the person you chat with; 404 for any other id or a missing file.
    The browser may cache it for a day, privately (never on shared caches)."""
    if user_id == user["id"]:
        name = user["username"]
    else:
        peer = get_peer(db, user["id"])
        if not peer or peer["id"] != user_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "No avatar")
        name = peer["username"]

    path = (AVATAR_DIR / f"{name.lower()}.jpg").resolve()
    if path.parent != AVATAR_DIR or not path.is_file():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No avatar")
    return FileResponse(path, media_type="image/jpeg",
                        headers={"Cache-Control": "private, max-age=86400"})
