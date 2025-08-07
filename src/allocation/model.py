import datetime
from typing import List, Self, Set

from pydantic import BaseModel


class OrderLine(BaseModel):
    model_config = {"frozen": True}

    reference: str
    sku: str
    quantity: int


class Order(BaseModel):
    reference: str
    order_lines: List[OrderLine]


class Batch(BaseModel):
    reference: str
    sku: str
    purchased_quantity: int

    eta: datetime.date | None

    _allocations: Set[OrderLine] = set()

    def allocate(self, order_line: OrderLine) -> None:
        """Allocate an order_line from the batch"""
        if self.can_allocate(order_line):
            self._allocations.add(order_line)

    def deallocate(self, order_line: OrderLine) -> None:
        """Remove order_line allocation from this batch

        Args:
            order_line:

        Returns:
            stock allocated
        """
        if order_line in self._allocations:
            self._allocations.remove(order_line)

    @property
    def allocated_quantity(self) -> int:
        """Amount of stock allocated

        Returns:

        """
        return sum(line.quantity for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        """Quantity available"""
        return self.purchased_quantity - self.allocated_quantity

    def can_allocate(self, order_line: OrderLine) -> bool:
        """Checks whether an order_line can be allocated from this batch

        Args:
            order_line: Order line to be allocated

        Returns:
            Truthy
        """
        return order_line.sku == self.sku and self.available_quantity >= order_line.quantity

    def __gt__(self, other: Self) -> bool:
        if self.eta is None:
            return False
        if other.eta is None:
            return True

        return self.eta > other.eta
