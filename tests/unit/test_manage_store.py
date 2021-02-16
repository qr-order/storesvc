from storesvc.domain.model import Store, Item


def test_add_item():
    store = Store(name="Starbucks")
    item = Item(name="Americano", price=5000, quantity=100)

    item_id = store.add_item(item)

    assert item_id == item.id
    assert store.list_items() == [item]


def test_get_item():
    store = Store(name="Starbucks")
    item = Item(name="Americano", price=5000, quantity=100)
    item_id = store.add_item(item)

    result = store.get_item(item_id)

    assert result == item


def test_get_time_return_none_if_not_exists():
    store = Store(name="Starbucks")
    item = Item(name="Americano", price=5000, quantity=100)

    result = store.get_item(item.id)

    assert result is None


def list_items():
    store = Store(name="Starbucks")
    store.add_item(Item(name="Americano", price=5000, quantity=100))
    store.add_item(Item(name="CafeLatte", price=5500, quantity=50))

    result = store.list_items()

    assert len(result) == 2


def test_delete_item():
    store = Store(name="Starbucks")
    item = Item(name="Americano", price=5000, quantity=100)
    store.add_item(item)

    result = store.delete_item(item)

    assert result == item
    assert len(store.list_items()) == 0


def test_set_item_quantity():
    store = Store(name="Starbucks")
    item = Item(name="Americano", price=5000, quantity=100)
    item_id = store.add_item(item)

    store.set_item_quantity(item_id, 150)

    assert store.get_item(item_id).quantity == 150
