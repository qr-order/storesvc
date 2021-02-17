import pytest
from datetime import datetime

from storesvc.domain.model import Store, Item, Order, OrderStatus
from storesvc.service_layer import unit_of_work


def insert_store(session, store: Store):
    session.execute(
        'INSERT INTO stores (id, name)'
        ' VALUES (:id, :name)',
        dict(id=store.id, name=store.name)
    )
    for item in store.list_items():
        session.execute(
            'INSERT INTO items (id, name, price, quantity)'
            ' VALUES (:id, :name, :price, :quantity)',
            dict(id=item.id, name=item.name, price=item.price, quantity=item.quantity)
        )
        session.execute(
            'INSERT INTO store_items_mappings (store_id, item_id)'
            ' VALUES (:store_id, :item_id)',
            dict(store_id=store.id, item_id=item.id)
        )


def get_item_quantity(session, item_id: str):
    [[item_quantity]] = session.execute(
        'SELECT quantity FROM items WHERE id=:item_id',
        dict(item_id=item_id)
    )
    return item_quantity


def test_uow_can_retrieve_a_store_and_approve_an_order(session_factory):
    session = session_factory()
    store = Store(name='Store_001')
    item = Item(name='Item_001', price=1000.0, quantity=10)
    store.add_item(item)
    insert_store(session, store)

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        store = uow.stores.get(id=store.id)
        order = Order(order_id='o1', order_datetime=datetime.now(), customer_phone='010-1234-1234', store_id=store.id,
                      item_ids=[item.id], order_status=OrderStatus.PUBLISHED.value)
        store.approve(order)
        uow.commit()

    item_quantity = get_item_quantity(session, item.id)
    assert item_quantity == item.quantity - 1


def test_rolls_back_uncommitted_work_by_default(session_factory):
    store = Store(name='Store_001')
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        insert_store(uow.session, store)

    new_session = session_factory()
    rows = list(new_session.execute('SELECT * FROM "stores"'))
    assert rows == []


def test_rolls_back_on_error(session_factory):
    class TestException(Exception):
        pass

    store = Store(name='Store_001')
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with pytest.raises(TestException):
        with uow:
            insert_store(uow.session, store)
            raise TestException()

    new_session = session_factory()
    rows = list(new_session.execute('SELECT * FROM "stores"'))
    assert rows == []
