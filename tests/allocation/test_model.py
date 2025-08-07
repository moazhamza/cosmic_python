import json
from datetime import date
from typing import Tuple
from unittest import TestCase

from allocation.model import Batch, OrderLine


class TestAllocation(TestCase):
    @staticmethod
    def make_batch_and_line(sku: str, batch_qty: int, line_qty: int) -> Tuple[Batch, OrderLine]:
        return (
            Batch(
                reference="batch-001",
                sku=sku,
                purchased_quantity=batch_qty,
                eta=date.today(),
            ),
            OrderLine(reference="order-123", sku=sku, quantity=line_qty),
        )

    def test_allocating_to_a_batch_reduces_the_available_quantity(self) -> None:
        batch = Batch(
            reference="batch-001",
            sku="SMALL-TABLE",
            purchased_quantity=20,
            eta=date.today(),
        )
        order_line = OrderLine(reference="order-ref-1", sku="SMALL-TABLE", quantity=2)

        batch.allocate(order_line)

        self.assertEqual(batch.available_quantity, 18)

    def test_cannot_allocate_if_available_smaller_than_required(self) -> None:
        batch = Batch(
            reference="batch-002",
            sku="BLUE-CUSHION",
            purchased_quantity=1,
            eta=date.today(),
        )
        order_line = OrderLine(reference="order-ref-2", sku="BLUE-CUSHION", quantity=2)

        self.assertFalse(batch.can_allocate(order_line))

    def test_allocate_same_line_twice(self) -> None:
        batch = Batch(
            reference="batch-003",
            sku="BLUE-VASE",
            purchased_quantity=10,
            eta=date.today(),
        )
        order_line = OrderLine(reference="order-ref-3", sku="BLUE-VASE", quantity=2)

        # Allocate twice
        batch.allocate(order_line)
        batch.allocate(order_line)

        self.assertEqual(8, batch.available_quantity)

    def test_can_allocate_if_available_greater_than_required(self) -> None:
        batch = Batch(
            reference="batch-004",
            sku="SMALL-TABLE",
            purchased_quantity=20,
            eta=date.today(),
        )
        order_line = OrderLine(reference="order-ref-4", sku="SMALL-TABLE", quantity=5)

        batch.allocate(order_line)

    def test_can_allocate_if_available_equal_to_required(self) -> None:
        batch, line = self.make_batch_and_line("ELEGANT-LAMP", 2, 2)

        batch.allocate(line)

    def test_cannot_allocate_if_skus_do_not_match(self) -> None:
        batch = Batch(
            reference="batch-001",
            sku="UNCOMFORTABLE-CHAIR",
            purchased_quantity=100,
            eta=None,
        )
        different_sku_line = OrderLine(reference="order-123", sku="EXPENSIVE-TOASTER", quantity=10)
        self.assertFalse(batch.can_allocate(different_sku_line))

    def test_can_only_deallocate_allocated_lines(self) -> None:
        batch, unallocated_line = self.make_batch_and_line("DECORATIVE-TRINKET", 20, 2)
        batch.deallocate(unallocated_line)

        self.assertEqual(20, batch.available_quantity)

    def test_allocation_is_idempotent(self) -> None:
        batch, line = self.make_batch_and_line("ANGULAR-DESK", 20, 2)

        batch.allocate(line)
        batch.allocate(line)

        self.assertEqual(18, batch.available_quantity)

    def test_ingestion(self) -> None:
        batch_json = json.dumps(
            {
                "sku": "GREAT-LAMP",
                "reference": "batch-123",
                "purchased_quantity": 35,
                "eta": date.today().isoformat(),
            }
        )

        batch = Batch.model_validate_json(batch_json)

        self.assertEqual("GREAT-LAMP", batch.sku)
        self.assertEqual("batch-123", batch.reference)
        self.assertEqual(35, batch.purchased_quantity)
