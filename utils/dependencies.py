from typing import Generator

from database import SessionLocal


def get_db() -> Generator:
    """
    FastAPI dependency that yields a DB session and ensures it is closed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
