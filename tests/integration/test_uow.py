import pytest
import threading
import time
import traceback
from datetime import datetime
from typing import List

from storesvc.domain.model import Store, Item
from storesvc.domain.value import OrderStatus, Order
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


def try_to_approve(store_id: str, order: Order, exceptions):
    try:
        with unit_of_work.SqlAlchemyUnitOfWork() as uow:
            store = uow.stores.get(id=store_id)
            store.approve(order)
            time.sleep(0.2)
            uow.commit()
    except Exception as e:
        print(traceback.format_exc())
        exceptions.append(e)


def test_concurrent_approve_to_version_are_not_allowed(postgres_session_factory):
    store = Store(name='Store_001')
    item = Item(name='Itme_001', price=1000.0, quantity=10)
    store.add_item(item)
    session = postgres_session_factory()
    insert_store(session, store)
    session.commit()

    order1 = Order(
        order_id='o1',
        order_datetime=datetime.now(),
        customer_phone='01012341234',
        store_id=store.id,
        item_ids=[item.id],
        order_status=OrderStatus.PUBLISHED.value
    )
    order2 = Order(
        order_id='o2',
        order_datetime=datetime.now(),
        customer_phone='01012341234',
        store_id=store.id,
        item_ids=[item.id],
        order_status=OrderStatus.PUBLISHED.value
    )
    exceptions: List[Exception] = []
    try_to_approve_order1 = lambda: try_to_approve(store.id, order1, exceptions)
    try_to_approve_order2 = lambda: try_to_approve(store.id, order2, exceptions)
    thread1 = threading.Thread(target=try_to_approve_order1)
    thread2 = threading.Thread(target=try_to_approve_order2)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    [[version]] = session.execute(
        'SELECT version_number FROM stores WHERE id=:store_id',
        dict(store_id=store.id)
    )
    assert version == 1
    [exception] = exceptions
    assert 'could not serialize access due to concurrent update' in str(exception)

    [[quantity]] = session.execute(
        'SELECT quantity FROM items WHERE id=:item_id',
        dict(item_id=item.id)
    )
    assert quantity == item.quantity - 1

