import datetime
import pytest
from typing import List

from storesvc.domain import model
from storesvc.adapters import repository, provider
from storesvc.service_layer import services, unit_of_work


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


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self, repo=FakeRepository([])):
        self.stores = repo
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


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
        uow = FakeUnitOfWork(repo)
        prov = FakeOrderProvider([order])

        services.approve_order(order.order_id, uow, prov)
        store = uow.stores.get(store.id)
        item = store.get_item(item.id)
        assert item.quantity == 0
        assert uow.committed

    def test_approve_order_errors_for_invalid_store_id(self):
        store = model.Store(name='Store_001')
        item = model.Item(name='Item_001', price=1000.0, quantity=1)
        order = model.Order(
            order_id='o1',
            order_datetime=datetime.datetime.now(),
            customer_phone='01012341234',
            store_id=store.id,
            item_ids=['invalid_item_id'],
            order_status=model.OrderStatus.PUBLISHED.value
        )
        store.add_item(item)
        repo = FakeRepository([store])
        uow = FakeUnitOfWork(repo)
        prov = FakeOrderProvider([order])
        with pytest.raises(model.InvalidOrder, match="item does not exist"):
            services.approve_order(order.order_id, uow, prov)

    def test_approve_order_errors_for_invalid_store_id(self):
        store = model.Store(name='Store_001')
        order = model.Order(
            order_id='o1',
            order_datetime=datetime.datetime.now(),
            customer_phone='01012341234',
            store_id='invalid_store_id',
            item_ids=['invalid_item_id'],
            order_status=model.OrderStatus.PUBLISHED.value
        )
        repo = FakeRepository([store])
        uow = FakeUnitOfWork(repo)
        prov = FakeOrderProvider([order])

        with pytest.raises(model.InvalidOrder, match="store id is not matched"):
            services.approve_order(order.order_id, uow, prov)

    def test_approve_order_errors_for_invalid_store_id(self):
        store = model.Store(name='Store_001')
        item = model.Item(name='Item_001', price=1000.0, quantity=1)
        order = model.Order(
            order_id='o1',
            order_datetime=datetime.datetime.now(),
            customer_phone='01012341234',
            store_id=store.id,
            item_ids=[item.id, item.id],
            order_status=model.OrderStatus.PUBLISHED.value
        )
        store.add_item(item)
        repo = FakeRepository([store])
        uow = FakeUnitOfWork(repo)
        prov = FakeOrderProvider([order])
        with pytest.raises(model.OutOfStock, match="Out of stock for store_id"):
            services.approve_order(order.order_id, uow, prov)

    def test_approve_order_errors_for_invalid_order_status(self):
        store = model.Store(name='Store_001')
        item = model.Item(name='Item_001', price=1000.0, quantity=1)
        order = model.Order(
            order_id='o1',
            order_datetime=datetime.datetime.now(),
            customer_phone='01012341234',
            store_id=store.id,
            item_ids=[item.id, item.id],
            order_status=model.OrderStatus.APPROVED.value
        )
        store.add_item(item)
        repo = FakeRepository([store])
        uow = FakeUnitOfWork(repo)
        prov = FakeOrderProvider([order])
        with pytest.raises(model.InvalidOrder, match="The order cannot be approved"):
            services.approve_order(order.order_id, uow, prov)
