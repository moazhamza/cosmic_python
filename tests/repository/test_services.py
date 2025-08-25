import pytest

from src.allocation import model
from src.repository import repository
from src.allocation import service


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_returns_allocation():
    line = model.OrderLine(order_id="o1", sku="COMPLICATED-LAMP", quantity=10)
    batch = model.Batch(reference="b1", sku="COMPLICATED-LAMP", purchased_quantity=100, eta=None)
    repo = FakeRepository([batch])

    result = service.allocate(line, repo, FakeSession())
    assert result == "b1"


def test_error_for_invalid_sku():
    line = model.OrderLine(order_id="o1", sku="NONEXISTENTSKU", quantity=10)
    batch = model.Batch(reference="b1", sku="AREALSKU", purchased_quantity=100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(service.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        service.allocate(line, repo, FakeSession())


def test_commits():
    line = model.OrderLine(order_id="o1", sku="OMINOUS-MIRROR", quantity=10)
    batch = model.Batch(reference="b1", sku="OMINOUS-MIRROR", purchased_quantity=100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    service.allocate(line, repo, session)
    assert session.committed is True


def test_deallocate_decrements_available_quantity():
    repo, session = FakeRepository([]), FakeSession()
    # TODO: you'll need to implement the services.add_batch method
    service.add_batch("b1", "BLUE-PLINTH", 100, None, repo, session)
    line = model.OrderLine(order_id="o1", sku="BLUE-PLINTH", quantity=10)
    service.allocate(line, repo, session)
    batch = repo.get(reference="b1")
    assert batch.available_quantity == 90
    service.deallocate(...)
    assert batch.available_quantity == 100


def test_deallocate_decrements_correct_quantity(): ...  #  TODO - check that we decrement the right sku


def test_trying_to_deallocate_unallocated_batch(): ...  #  TODO: should this error or pass silently? up to you.
