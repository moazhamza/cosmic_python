from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars

from src.allocation.dependencies import get_repository
from src.allocation.exceptions import OutOfStock
from src.allocation.model import OrderLine
from src.allocation.service import InvalidSku, allocate
from src.repository.repository import SqlAlchemyRepository


logger = structlog.get_logger()
router = APIRouter(prefix="/batch")


@router.post("/allocate", status_code=status.HTTP_201_CREATED)
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

    repository.list()
    await logger.ainfo("Allocation request")

    for line in order_lines:
        try:
            allocate(line, repository, repository.session)
        except (OutOfStock, InvalidSku):
            await logger.awarning("Out of stock for line %s, not allocation", line)
            raise HTTPException(status_code=400, detail=f"Out of stock for sku {line.sku}")

    await logger.ainfo("Allocated request")
