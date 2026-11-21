"""FastAPI entry point: opens the Postgres pool on startup, mounts the API, serves the built frontend.
Run `npm run build` in frontend/ first; the "/" mount must stay last or it swallows /api routes."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .db import close_pool, open_pool
from .routers import auth, avatars, messages

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(_: FastAPI):
    open_pool()
    yield
    close_pool()


app = FastAPI(title="Chat backend", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(messages.router)
app.include_router(avatars.router)
if FRONTEND_DIR.is_dir():  # absent on API-only hosts (e.g. Railway), where Vercel serves the UI
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
