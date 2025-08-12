from typing import List

from src.allocation.exceptions import OutOfStock
from src.allocation.model import Batch, OrderLine


def allocate(order_line: OrderLine, batches: List[Batch]) -> str | None:
    """Allocates an order line to one of the batches in batches"""
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(order_line))

        batch.allocate(order_line)

        return batch.reference

    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {order_line.sku}")
