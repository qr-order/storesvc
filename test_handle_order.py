from datetime import datetime
from typing import List
from uuid import uuid4

from model import Item, Store, Order, OrderStatus


def make_store(items: List[Item]):
    store = Store(name="Store_001")
    for item in items:
        store.add_item(item)
    return store


def test_approved_an_order_reduces_item_quantity():
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

    store.approved(order)

    assert store.get_item(item.id).quantity == 9


def make_store_and_order(item_quantity: int, order_quantity: int, order_store_id: uuid4 = None):
    item = Item(name="Item_001", price=5000, quantity=item_quantity)
    store = make_store([item])
    order = Order(
        order_id="order_id_001",
        order_datetime=datetime.now(),
        customer_phone="000-0000-0000",
        store_id=order_store_id or store.id,
        item_ids=[item.id for _ in range(order_quantity)],
        order_status=OrderStatus.PUBLISHED.value
    )
    return store, order


def test_can_approved_if_item_quantity_greater_than_ordered():
    large_store, small_order = make_store_and_order(5, 4)
    assert large_store.can_approved(small_order)


def test_cannot_approved_if_item_quantity_smaller_than_ordered():
    small_store, large_order = make_store_and_order(4, 5)
    assert small_store.can_approved(large_order) is False


def test_cannot_approved_if_item_quantity_equal_to_ordered():
    store, order = make_store_and_order(5, 5)
    assert store.can_approved(order)


def test_cannot_approved_if_store_id_do_not_match():
    store, mismatched_order = make_store_and_order(5, 5, uuid4())
    assert store.can_approved(mismatched_order) is False
