from src.allocation import model
from src.allocation.model import OrderLine
from src.repository.repository import AbstractRepository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    """Check if the SKU is valid by checking against the list of batches"""
    return sku in {b.sku for b in batches}


def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    """Allocate a line to a batch"""
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref


def add_batch(param, param1, param2, param3, repo, session):
    return None


def deallocate(param):
    return None
