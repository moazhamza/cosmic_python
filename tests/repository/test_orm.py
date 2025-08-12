from datetime import date
from unittest import TestCase

from sqlmodel import create_engine, SQLModel, Session, text, select

from src.allocation.model import OrderLine, Batch


class TestORM(TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:", echo=True)
        SQLModel.metadata.create_all(bind=engine)
        self.session = Session(engine)

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    def test_orderline_mapper_can_load_lines(self):
        self.session.exec(
            text(
                "INSERT INTO orderline (order_id, sku, quantity) VALUES "
                '("order1", "RED-CHAIR", 12),'
                '("order2", "RED-TABLE", 13),'
                '("order3", "BLUE-LIPSTICK", 14)'
            )
        )
        expected = [
            OrderLine(order_id="order1", sku="RED-CHAIR", quantity=12),
            OrderLine(order_id="order2", sku="RED-TABLE", quantity=13),
            OrderLine(order_id="order3", sku="BLUE-LIPSTICK", quantity=14),
        ]
        result = self.session.exec(select(OrderLine)).all()

        # self.assertListEqual(expected, result)

        for expected_line, resulting_line in zip(expected, result):
            self.assertEqual(expected_line.order_id, resulting_line.order_id)
            self.assertEqual(expected_line.sku, resulting_line.sku)
            self.assertEqual(expected_line.quantity, resulting_line.quantity)

    def test_orderline_mapper_can_save_lines(self):
        new_line = OrderLine(order_id="order1", sku="DECORATIVE-WIDGET", quantity=12)
        self.session.add(new_line)
        self.session.commit()

        rows = list(self.session.exec(text('SELECT order_id, sku, quantity FROM "orderline"')))
        self.assertListEqual(rows, [("order1", "DECORATIVE-WIDGET", 12)])

    def test_retrieving_batches(self):
        self.session.exec(
            text(
                "INSERT INTO batch (reference, sku, purchased_quantity, eta)"
                ' VALUES ("batch1", "sku1", 100, null)'
            )
        )
        self.session.exec(
            text(
                "INSERT INTO batch (reference, sku, purchased_quantity, eta)"
                ' VALUES ("batch2", "sku2", 200, "2011-04-11")'
            )
        )
        expected = [
            Batch(reference="batch1", sku="sku1", purchased_quantity=100, eta=None),
            Batch(reference="batch2", sku="sku2", purchased_quantity=200, eta=date(2011, 4, 11)),
        ]

        self.assertListEqual(
            [x.model_dump() for x in expected],
            [x.model_dump() for x in list(self.session.exec(select(Batch)).all())],
        )

    def test_saving_batches(self):
        batch = Batch(reference="batch1", sku="sku1", purchased_quantity=100, eta=None)
        self.session.add(batch)
        self.session.commit()
        rows = self.session.exec(
            text('SELECT reference, sku, purchased_quantity, eta FROM "batch"')
        )
        self.assertListEqual(list(rows), [("batch1", "sku1", 100, None)])

    def test_saving_allocations(self):
        batch = Batch(reference="batch1", sku="sku1", purchased_quantity=100, eta=None)
        line = OrderLine(id="order1", sku="sku1", quantity=10)
        batch.allocate(line)
        self.session.add(batch)
        self.session.commit()
        rows = list(self.session.exec(text('SELECT orderline_id, batch_id FROM "allocations"')))
        assert rows == [(line.id, batch.reference)]
