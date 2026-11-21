"""FastAPI entry point: creates the DB tables on startup, mounts the API, serves the built frontend.
Run `npm run build` in frontend/ first; the "/" mount must stay last or it swallows /api routes."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .db import init_db
from .routers import auth, messages

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Chat backend", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(messages.router)
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
