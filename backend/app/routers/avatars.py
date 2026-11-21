"""Profile pictures at /api/avatars/{user_id}, served only to a logged-in user (you or your peer).
Images live in the avatars table (uploaded with scripts/set_avatar.py), so they deploy with the DB."""
from fastapi import APIRouter, Depends, Header, HTTPException, Response, status

from .. import security
from ..db import Conn, get_db
from ..users import get_peer

router = APIRouter(prefix="/api/avatars", tags=["avatars"])


@router.get("/{user_id}")
def avatar(user_id: int, if_none_match: str | None = Header(default=None),
           user: dict = Depends(security.current_user), db: Conn = Depends(get_db)):
    """Image for you or the person you chat with; 404 for any other id or no avatar set.
    Cached privately for an hour; the ETag changes when the image is replaced."""
    if user_id != user["id"]:
        peer = get_peer(db, user["id"])
        if not peer or peer["id"] != user_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "No avatar")

    meta = db.execute("SELECT content_type, extract(epoch FROM updated_at) AS v "
                      "FROM avatars WHERE user_id = %s", (user_id,)).fetchone()
    if not meta:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No avatar")
    headers = {"Cache-Control": "private, max-age=3600", "ETag": f'"{user_id}-{meta["v"]}"'}
    if if_none_match == headers["ETag"]:
        return Response(status_code=status.HTTP_304_NOT_MODIFIED, headers=headers)

    image = db.execute("SELECT image FROM avatars WHERE user_id = %s", (user_id,)).fetchone()
    return Response(content=bytes(image["image"]), media_type=meta["content_type"],
                    headers=headers)
