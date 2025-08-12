from typing import Annotated, List

from fastapi import APIRouter, Depends, status
import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars

from allocation.dependencies import get_repository
from allocation.exceptions import OutOfStock
from allocation.model import OrderLine
from allocation.service import allocate
from repository.repository import SqlAlchemyRepository


logger = structlog.get_logger()
router = APIRouter(prefix="/batch")


@router.put("/allocate", status_code=status.HTTP_201_CREATED)
async def allocate_endpoint(
    order_lines: List[OrderLine],
    repository: Annotated[SqlAlchemyRepository, Depends(get_repository)],
) -> None:
    """Allocates a list of OrderLine objects to a batch

    Args:
        order_lines:
        repository

    Returns:

    """
    clear_contextvars()
    bind_contextvars(order_lines=order_lines)

    batches = repository.list()
    await logger.ainfo("Allocation request")

    for line in order_lines:
        try:
            allocate(line, batches)
        except OutOfStock:
            await logger.awarning("Out of stock for line %s, not allocation", line)
            continue

    await logger.ainfo("Allocated request")
