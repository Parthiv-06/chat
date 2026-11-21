"""Chat endpoints under /api/messages: load the conversation with the other user, and send.
Clients poll GET with ?after=<last id they have> to pick up new messages; ids only ever grow."""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from .. import security
from ..db import Conn, get_db
from ..schemas import MessageIn, MessageList, MessageOut
from ..users import get_peer

router = APIRouter(prefix="/api/messages", tags=["messages"])

COLUMNS = "id, sender_id, recipient_id, body, created_at"
BETWEEN = ("((sender_id = %(me)s AND recipient_id = %(peer)s) "
           "OR (sender_id = %(peer)s AND recipient_id = %(me)s))")


@router.get("", response_model=MessageList)
def list_messages(after: int | None = Query(default=None, ge=0),
                  limit: int = Query(default=200, ge=1, le=500),
                  user: dict = Depends(security.current_user),
                  db: Conn = Depends(get_db)):
    """Oldest-first messages between you and the other user.
    Without `after` you get the latest `limit`; with it, only messages newer than that id."""
    peer = get_peer(db, user["id"])
    if not peer:
        return {"messages": []}
    params = {"me": user["id"], "peer": peer["id"], "after": after, "limit": limit}
    if after is None:
        rows = db.execute(f"SELECT {COLUMNS} FROM messages WHERE {BETWEEN} "
                          "ORDER BY id DESC LIMIT %(limit)s", params).fetchall()[::-1]
    else:
        rows = db.execute(f"SELECT {COLUMNS} FROM messages WHERE {BETWEEN} "
                          "AND id > %(after)s ORDER BY id LIMIT %(limit)s", params).fetchall()
    return {"messages": rows}


@router.post("", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def send_message(body: MessageIn, user: dict = Depends(security.current_user),
                 db: Conn = Depends(get_db)):
    """Stores a message from you to the other user and returns it with its id and time."""
    peer = get_peer(db, user["id"])
    if not peer:
        raise HTTPException(status.HTTP_409_CONFLICT, "No other user to message yet")
    return db.execute(f"INSERT INTO messages (sender_id, recipient_id, body) "
                      f"VALUES (%s, %s, %s) RETURNING {COLUMNS}",
                      (user["id"], peer["id"], body.body)).fetchone()
