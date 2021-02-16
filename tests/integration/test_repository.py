from storesvc.domain import model
from storesvc.adapters import repository


def test_repository_can_save_a_store(session):
    store = model.Store(name='Store_001')

    repo = repository.SqlAlchemyRepository(session)
    repo.new(store)
    session.commit()

    rows = list(session.execute(
        'SELECT id, name FROM "stores"'
    ))
    assert rows == [(store.id, store.name)]


def insert_store_with_item(session, store: model.Store, item: model.Item):
    store.add_item(item)
    session.add(store)
    session.commit()
    return store


def test_repository_can_retrieve_a_store_with_mapping_items(session):
    store = insert_store_with_item(
        session, model.Store(name='Store_001'), model.Item(name='Item_001', price=1000.0, quantity=1)
    )
    repo = repository.SqlAlchemyRepository(session)
    retrieved = repo.get(store.id)

    assert retrieved == store
    assert retrieved._items == store._items
