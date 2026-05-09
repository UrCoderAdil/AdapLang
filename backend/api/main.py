"""FastAPI application entry point."""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import quiz, user, game, irt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from ..db.database import create_tables
    try:
        create_tables()
        logger.info("Database tables verified.")
    except Exception as exc:
        logger.warning("Could not connect to DB at startup (is Postgres running?): %s", exc)
    yield


app = FastAPI(
    title="AdapLang — Adaptive Language RPG API",
    description="IRT-powered adaptive language learning RPG backend.",
    version="1.0.0",
    lifespan=lifespan,
)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quiz.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(game.router, prefix="/api")
app.include_router(irt.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "AdapLang API is running.", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
