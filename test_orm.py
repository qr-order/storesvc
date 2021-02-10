import model


def test_item_mapper_can_load_items(session):
    expected = [
        model.Item(name="Item_001", price=1000.0, quantity=10),
        model.Item(name="Item_002", price=2000.0, quantity=20),
        model.Item(name="Item_003", price=3000.0, quantity=30),
    ]
    session.execute(
        'INSERT INTO items (id, name, price, quantity) VALUES '
        f'("{expected[0].id}", "{expected[0].name}", "{expected[0].price}", {expected[0].quantity}),'
        f'("{expected[1].id}", "{expected[1].name}", "{expected[1].price}", {expected[1].quantity}),'
        f'("{expected[2].id}", "{expected[2].name}", "{expected[2].price}", {expected[2].quantity})'
    )
    assert session.query(model.Item).all() == expected


def test_item_mapper_can_save_items(session):
    new_item = model.Item(name="Item_001", price=1000.0, quantity=10)
    session.add(new_item)
    session.commit()

    rows = list(session.execute('SELECT id, name, price, quantity FROM "items"'))
    assert rows == [(new_item.id, new_item.name, new_item.price, new_item.quantity)]


def test_retrieving_stores(session):
    expected = [
        model.Store(name='Store_001'),
        model.Store(name='Store_002'),
    ]
    session.execute(
        'INSERT INTO stores (id, name) VALUES '
        f'("{expected[0].id}", "{expected[0].name}"),'
        f'("{expected[1].id}", "{expected[1].name}")'
    )
    assert session.query(model.Store).all() == expected


def test_saving_stores(session):
    new_store = model.Store(name='Store_001')
    session.add(new_store)
    session.commit()
    rows = list(session.execute('SELECT id, name FROM "stores"'))
    assert rows == [(new_store.id, new_store.name)]


def test_retrieving_store_item_mappings(session):
    new_item = model.Item(name="Item_001", price=1000.0, quantity=10)
    new_store = model.Store(name='Store_001')
    new_store.add_item(new_item)
    session.add(new_item)
    session.add(new_store)

    store = session.query(model.Store).one()

    assert store._items == [new_item]
