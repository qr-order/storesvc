import pytest
from datetime import datetime
from typing import List
from uuid import uuid4

from storesvc.domain.model import Item, Store, Order, OrderStatus, OutOfStock, InvalidOrder


def make_store(items: List[Item]):
    store = Store(name="Store_001")
    for item in items:
        store.add_item(item)
    return store


def test_approve_an_order_reduces_item_quantity():
    item = Item(name="Item_001", price=5000, quantity=10)
    store = make_store([item])

    order = Order(
        order_id="order_id_001",
        order_datetime=datetime.now(),
        customer_phone="000-0000-0000",
        store_id=store.id,
        item_ids=[item.id],
        order_status=OrderStatus.PUBLISHED.value
    )

    store.approve(order)

    assert store.get_item(item.id).quantity == 9


def make_store_and_order(item_quantity: int, order_quantity: int, order_store_id: uuid4 = None, status=None):
    item = Item(name="Item_001", price=5000, quantity=item_quantity)
    store = make_store([item])
    order = Order(
        order_id="order_id_001",
        order_datetime=datetime.now(),
        customer_phone="000-0000-0000",
        store_id=order_store_id or store.id,
        item_ids=[item.id for _ in range(order_quantity)],
        order_status=status or OrderStatus.PUBLISHED.value
    )
    return store, order


def test_can_approve_if_quantity_equal_to_ordered():
    store, order = make_store_and_order(5, 5)
    store.approve(order)


def test_raise_out_of_stock_exception_if_quantity_smaller_than_ordered():
    small_store, large_order = make_store_and_order(4, 5)
    with pytest.raises(OutOfStock, match=large_order.order_id):
        small_store.approve(large_order)


def test_raise_invalid_order_if_store_id_is_not_matched():
    store, mismatched_order = make_store_and_order(5, 5, uuid4())
    with pytest.raises(InvalidOrder, match=mismatched_order.order_id):
        store.approve(mismatched_order)


def test_raise_invalid_order_if_item_does_not_exist():
    store, order = make_store_and_order(5, 5)
    item = store.list_items()[0]
    store.delete_item(item)
    with pytest.raises(InvalidOrder, match=order.order_id):
        store.approve(order)


def test_raise_invalid_order_if_order_is_not_published():
    store, approved_order = make_store_and_order(5, 5, uuid4(), OrderStatus.APPROVED.value)
    with pytest.raises(InvalidOrder, match=approved_order.order_id):
        store.approve(approved_order)
