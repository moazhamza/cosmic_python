from typing import Any, Generator

from config.settings import settings
from sqlmodel import Session, SQLModel, create_engine


sqlite_file_name = "database.db"
sqlite_url = settings.DATABASE_URL

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    """Create the tables"""
    SQLModel.metadata.create_all(engine)


def drop_tables():
    """Drop the tables for the next run"""
    SQLModel.metadata.drop_all(bind=engine)


def get_db_session() -> Generator[Session, Any, None]:
    """Returns a Session for the DB"""
    with Session(engine) as session:
        yield session
