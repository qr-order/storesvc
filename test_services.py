import datetime
from typing import List

import model
import provider
import repository
import services


class FakeSession():
    committed = False

    def commit(self):
        self.committed = True


class FakeOrderProvider(provider.AbstractOrderProvider):
    def __init__(self, orders: List[model.Order] = list()):
        self._orders = orders

    def get_order(self, order_id: str) -> model.Order:
        return next(order for order in self._orders if order.order_id == order_id)

    def list_orders(self, store_id: str) -> List[model.Order]:
        return [order for order in self._orders if order.store_id == store_id]


class FakeRepository(repository.AbstractRepository):
    def __init__(self, stores: List[model.Store] = list()):
        self._stores = stores

    def new(self, store: model.Store):
        self._stores.append(store)

    def get(self, id: str) -> model.Store:
        return next(store for store in self._stores if store.id == id)


class TestApproveOrderService:
    def test_approve_order_reduces_item_quantity(self):
        store = model.Store(name='Store_001')
        item = model.Item(name='Item_001', price=1000.0, quantity=1)
        order = model.Order(
            order_id='o1',
            order_datetime=datetime.datetime.now(),
            customer_phone='01012341234',
            store_id=store.id,
            item_ids=[item.id],
            order_status=model.OrderStatus.PUBLISHED.value
        )
        store.add_item(item)
        repo = FakeRepository([store])
        prov = FakeOrderProvider([order])

        services.approve_order(order.order_id, repo, prov, FakeSession())
        store = repo.get(store.id)
        item = store.get_item(item.id)
        assert item.quantity == 0

    def test_commits(self):
        store = model.Store(name='Store_001')
        item = model.Item(name='Item_001', price=1000.0, quantity=1)
        order = model.Order(
            order_id='o1',
            order_datetime=datetime.datetime.now(),
            customer_phone='01012341234',
            store_id=store.id,
            item_ids=[item.id],
            order_status=model.OrderStatus.PUBLISHED.value
        )
        store.add_item(item)
        repo = FakeRepository([store])
        prov = FakeOrderProvider([order])
        session = FakeSession()

        services.approve_order(order.order_id, repo, prov, session)
        assert session.committed is True
