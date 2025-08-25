import abc
from typing import List

from sqlmodel import Session, select

from src.allocation.model import Batch


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, reference_number: str) -> Batch:
        """Retrieves a Batch object using the reference number

        Args:
            reference_number: the reference number associated with the object to look up

        Returns:
            The batch object associated with the reference number
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add(self, batch_obj: Batch) -> None:
        """Adds a batch object to the repository

        Args:
            batch_obj: Object to add
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> List[Batch]:
        """lists all batch objects in repository"""
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session) -> None:
        """Initializes the Session to be used with the Repository

        Args:
            session:
        """
        self.session = session

    def get(self, reference: str) -> Batch:
        """Gets a batch object from a SqlAlchemy backed repository

        Args:
            reference:

        Returns:

        """
        return self.session.exec(select(Batch).where(Batch.reference == reference)).one()

    def add(self, batch_obj: Batch) -> None:
        """Adds a batch object to a sqlalchemy backed repository

        Args:
            batch_obj:

        Returns:

        """
        self.session.add(batch_obj)

    def list(self) -> List[Batch]:
        """Retrieves all batch objects in the repository

        Returns:

        """
        return list(self.session.exec(select(Batch)).all())
