from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.repository.dependencies import get_db_session
from src.repository.repository import SqlAlchemyRepository


def get_repository(session: Annotated[Session, Depends(get_db_session)]) -> SqlAlchemyRepository:
    """Retrieves a repository"""
    return SqlAlchemyRepository(session)
