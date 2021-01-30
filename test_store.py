import pytest

from model import Store, Item


def test_add_items():
    store = Store(name="Starbucks")
    item = Item(
        name="Americano",
        price=5000,
        quantity=100,
    )

    store.add_items([item])

    assert store.list_items() == [item]
