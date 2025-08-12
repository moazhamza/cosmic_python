from unittest import TestCase

from sqlmodel import create_engine, text, SQLModel, Session

from src.allocation.model import Batch
from src.repository.repository import SqlAlchemyRepository


class TestRepository(TestCase):
    @staticmethod
    def get_session():
        engine = create_engine("sqlite:///:memory:", echo=True)
        SQLModel.metadata.create_all(engine)
        session = Session(bind=engine)
        return session

    def setUp(self):
        self.session = self.get_session()

    def tearDown(self):
        self.session.close()

    def insert_order_line(self):
        sql_text = text(
            'INSERT INTO "orderline" (order_id, sku, quantity) VALUES ("order1", "GENERIC-SOFA", 12)'
        )
        self.session.exec(sql_text)

        [[orderline_id]] = self.session.execute(
            text("SELECT id FROM orderline WHERE order_id=:order_id AND sku=:sku"),
            dict(order_id="order1", sku="GENERIC-SOFA"),
        )
        return orderline_id

    def insert_batch(self, batch_id):
        self.session.execute(
            text(
                "INSERT INTO batch (reference, sku, purchased_quantity, eta) "
                ' VALUES (:batch_id, "GENERIC-SOFA", 100, null)',
            ),
            dict(batch_id=batch_id, sku="GENERIC-SOFA", purchased_quantity=100),
        )
        [[batch_id]] = self.session.execute(
            text('SELECT reference FROM batch WHERE reference=:batch_id AND sku="GENERIC-SOFA"'),
            dict(batch_id=batch_id),
        )
        return batch_id

    def insert_allocation(self, orderline_id, batch_id):
        self.session.execute(
            text(
                "INSERT INTO allocations (orderline_id, batch_id) VALUES (:orderline_id, :batch_id)"
            ),
            dict(orderline_id=orderline_id, batch_id=batch_id),
        )

    def test_repository_can_save_a_batch(self):
        batch = Batch(reference="batch-1", sku="RUSTY-SOAPDISH", purchased_quantity=100, eta=None)

        repo = SqlAlchemyRepository(self.session)

        repo.add(batch)
        self.session.commit()
        rows = self.session.exec(
            text('SELECT reference, sku, purchased_quantity, eta FROM "batch"')
        )

        self.assertListEqual([("batch-1", "RUSTY-SOAPDISH", 100, None)], list(rows))

    def test_repository_can_retrieve_a_batch_with_allocations(self):
        orderline_id = self.insert_order_line()

        batch1_id = self.insert_batch("batch1")

        self.insert_batch("batch2")
        self.insert_allocation(orderline_id, batch1_id)

        repo = SqlAlchemyRepository(self.session)
        retrieved = repo.get("batch1")

        expected = Batch(reference="batch1", sku="GENERIC-SOFA", purchased_quantity=100, eta=None)

        # self.assertEqual(expected, retrieved)
        self.assertEqual(expected.sku, retrieved.sku)
        self.assertEqual(expected.purchased_quantity, retrieved.purchased_quantity)
