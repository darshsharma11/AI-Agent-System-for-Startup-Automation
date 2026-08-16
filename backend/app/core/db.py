"""
SQLAlchemy engine, session factory, and declarative base.

Works with SQLite locally (``sqlite:///./app.db``) and PostgreSQL in
production — the only thing that changes is the ``DATABASE_URL`` env var.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# ── Engine ───────────────────────────────────────────────────────────────
# SQLite needs ``check_same_thread=False`` so FastAPI's thread-pool
# workers can share the connection.  PostgreSQL ignores this kwarg.
_connect_args: dict = {}
if settings.DATABASE_URL.startswith("sqlite"):
    _connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=_connect_args,
    echo=False,
)

# ── Session factory ──────────────────────────────────────────────────────
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Declarative base ────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


# ── Dependency for FastAPI routes ────────────────────────────────────────
def get_db():
    """
    Yield a SQLAlchemy session to a FastAPI route and guarantee it is
    closed afterwards, even on exceptions.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
