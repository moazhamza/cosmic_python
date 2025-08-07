import datetime
from datetime import timedelta
from unittest import TestCase

from allocation.allocate import allocate
from allocation.exceptions import OutOfStock
from allocation.model import Batch, OrderLine


class TestAllocate(TestCase):
    def test_prefers_current_stock_batches_to_shipments(self):
        in_stock_batch = Batch(
            reference="in-stock-batch", sku="RETRO-CLOCK", purchased_quantity=100, eta=None
        )
        shipment_batch = Batch(
            reference="shipment-batch",
            sku="RETRO-CLOCK",
            purchased_quantity=100,
            eta=datetime.date.today() + timedelta(days=1),
        )

        line = OrderLine(reference="oref", sku="RETRO-CLOCK", quantity=10)

        allocate(line, [in_stock_batch, shipment_batch])

        self.assertEqual(90, in_stock_batch.available_quantity)
        self.assertEqual(100, shipment_batch.available_quantity)

    def test_prefers_earlier_batches(self):
        earliest = Batch(
            reference="speedy-batch",
            sku="MINIMALIST-SPOON",
            purchased_quantity=100,
            eta=datetime.date.today(),
        )
        medium = Batch(
            reference="normal-batch",
            sku="MINIMALIST-SPOON",
            purchased_quantity=100,
            eta=datetime.date.today() + timedelta(days=1),
        )
        latest = Batch(
            reference="slow-batch",
            sku="MINIMALIST-SPOON",
            purchased_quantity=100,
            eta=datetime.date.today() + timedelta(days=10),
        )
        line = OrderLine(reference="order1", sku="MINIMALIST-SPOON", quantity=10)

        allocate(line, [medium, earliest, latest])

        self.assertEqual(90, earliest.available_quantity)
        self.assertEqual(100, medium.available_quantity)
        self.assertEqual(100, latest.available_quantity)

    def test_returns_allocated_batch_ref(self):
        in_stock_batch = Batch(
            reference="in-stock-batch-ref", sku="HIGHBROW-POSTER", purchased_quantity=100, eta=None
        )
        shipment_batch = Batch(
            reference="shipment-batch-ref",
            sku="HIGHBROW-POSTER",
            purchased_quantity=100,
            eta=datetime.date.today() + timedelta(days=1),
        )
        line = OrderLine(reference="oref", sku="HIGHBROW-POSTER", quantity=10)
        allocation = allocate(line, [in_stock_batch, shipment_batch])
        assert allocation == in_stock_batch.reference

    def test_raises_out_of_stock_exception_if_cannot_allocate(self):
        batch = Batch(
            reference="ref1", sku="small-fork", purchased_quantity=10, eta=datetime.date.today()
        )
        line1 = OrderLine(reference="order1", sku="small-fork", quantity=10)
        line2 = OrderLine(reference="order2", sku="small-fork", quantity=10)

        allocate(line1, [batch])

        with self.assertRaises(OutOfStock) as ctx:
            allocate(line2, [batch])
            self.assertIn("small-fork", str(ctx.exception))
