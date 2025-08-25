import datetime
from typing import List, Self

from sqlmodel import Field, Relationship, SQLModel

from src.allocation.exceptions import OutOfStock


class Allocation(SQLModel, table=True):
    batch_id: int = Field(default=None, foreign_key="batch.id", primary_key=True)
    orderline_id: int = Field(default=None, foreign_key="orderline.id", primary_key=True)


class OrderLine(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    sku: str
    quantity: int

    batch_id: int | None = Field(default=None, foreign_key="batch.id")
    batch: "Batch" = Relationship(back_populates="allocations", link_model=Allocation)
    order_id: str | None

    def __hash__(self):
        return hash(self.sku) + hash(self.sku) + hash(self.quantity)


class Batch(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    reference: str
    sku: str
    purchased_quantity: int

    eta: datetime.date | None

    allocations: List[OrderLine] = Relationship(
        back_populates="batch",
        sa_relationship_kwargs={"collection_class": set},
        link_model=Allocation,
    )

    def allocate(self, order_line: OrderLine) -> None:
        """Allocate an order_line from the batch"""
        if self.can_allocate(order_line):
            self.allocations.add(order_line)

    def deallocate(self, order_line: OrderLine) -> None:
        """Remove order_line allocation from this batch

        Args:
            order_line:

        Returns:
            stock allocated
        """
        if order_line in self.allocations:
            self.allocations.remove(order_line)

    @property
    def allocated_quantity(self) -> int:
        """Amount of stock allocated

        Returns:

        """
        return sum(line.quantity for line in self.allocations)

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


def allocate(line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")
