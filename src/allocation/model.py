import datetime
from typing import List, Self, Set

from sqlmodel import Field, Relationship, SQLModel


class Allocations(SQLModel, table=True):
    batch_id: str = Field(foreign_key="batch.reference", primary_key=True)
    orderline_id: str = Field(foreign_key="orderline.id", primary_key=True)


class OrderLine(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    sku: str
    quantity: int

    batch_id: str | None = Field(default=None, foreign_key="batch.reference")
    batch: "Batch" = Relationship(back_populates="allocations", link_model=Allocations)

    order_id: str | None

    def __hash__(self):
        return hash(self.sku) + hash(self.sku) + hash(self.quantity)


class Batch(SQLModel, table=True):
    reference: str | None = Field(default=None, primary_key=True)
    sku: str
    purchased_quantity: int

    eta: datetime.date | None

    allocations: List[OrderLine] = Relationship(back_populates="batch", link_model=Allocations)
    _allocations: Set[OrderLine] = set()

    def allocate(self, order_line: OrderLine) -> None:
        """Allocate an order_line from the batch"""
        if self.can_allocate(order_line):
            self._allocations.add(order_line)

        self.allocations = list(self._allocations)

    def deallocate(self, order_line: OrderLine) -> None:
        """Remove order_line allocation from this batch

        Args:
            order_line:

        Returns:
            stock allocated
        """
        if order_line in self.allocations:
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
