"""Chat endpoints under /api/messages: load the conversation with the other user, and send.
Clients poll GET with ?after=<last id they have> to pick up new messages; ids only ever grow."""
import sqlite3
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status

from .. import security
from ..db import get_db
from ..schemas import MessageIn, MessageList, MessageOut
from ..users import get_peer

router = APIRouter(prefix="/api/messages", tags=["messages"])

COLUMNS = "id, sender_id, recipient_id, body, created_at"
BETWEEN = "((sender_id = :me AND recipient_id = :peer) OR (sender_id = :peer AND recipient_id = :me))"


def _to_out(row: sqlite3.Row) -> MessageOut:
    return MessageOut(id=row["id"], sender_id=row["sender_id"], recipient_id=row["recipient_id"],
                      body=row["body"],
                      created_at=datetime.fromtimestamp(row["created_at"] / 1000, timezone.utc))


@router.get("", response_model=MessageList)
def list_messages(after: int | None = Query(default=None, ge=0),
                  limit: int = Query(default=200, ge=1, le=500),
                  user: sqlite3.Row = Depends(security.current_user),
                  db: sqlite3.Connection = Depends(get_db)):
    """Oldest-first messages between you and the other user.
    Without `after` you get the latest `limit`; with it, only messages newer than that id."""
    peer = get_peer(db, user["id"])
    if not peer:
        return {"messages": []}
    params = {"me": user["id"], "peer": peer["id"], "after": after, "limit": limit}
    if after is None:
        rows = db.execute(f"SELECT {COLUMNS} FROM messages WHERE {BETWEEN} "
                          "ORDER BY id DESC LIMIT :limit", params).fetchall()[::-1]
    else:
        rows = db.execute(f"SELECT {COLUMNS} FROM messages WHERE {BETWEEN} AND id > :after "
                          "ORDER BY id LIMIT :limit", params).fetchall()
    return {"messages": [_to_out(r) for r in rows]}


@router.post("", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def send_message(body: MessageIn,
                 user: sqlite3.Row = Depends(security.current_user),
                 db: sqlite3.Connection = Depends(get_db)):
    """Stores a message from you to the other user and returns it with its id and time."""
    peer = get_peer(db, user["id"])
    if not peer:
        raise HTTPException(status.HTTP_409_CONFLICT, "No other user to message yet")
    row = db.execute(f"INSERT INTO messages (sender_id, recipient_id, body) VALUES (?, ?, ?) "
                     f"RETURNING {COLUMNS}", (user["id"], peer["id"], body.body)).fetchone()
    return _to_out(row)
