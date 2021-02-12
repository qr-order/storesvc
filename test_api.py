import pytest
import requests
from uuid import uuid4

import config
import model


@pytest.mark.usefixtures('restart_api')
def test_api_returns_items(add_stores):
    store = model.Store(name='Store_001')
    items = [
        model.Item(name='Item_001', price=1000.0, quantity=10),
        model.Item(name='Item_002', price=2000.0, quantity=20),
    ]
    for item in items:
        store.add_item(item)
    add_stores([store])
    url = config.get_api_url()

    r = requests.get(f'{url}/stores/{store.id}/items')
    assert r.status_code == 200
    assert r.json()['storeId'] == store.id
    assert r.json()['storeName'] == store.name
    assert len(r.json()['items']) == 2
    assert r.json()['items'] == [
        {'id': item.id, 'name': item.name, 'price': item.price, 'quantity': item.quantity} for item in items
    ]


@pytest.mark.usefixtures('restart_api')
def test_invalid_store_id_returns_404_and_error_message(add_stores):
    store = model.Store(name='Store_001')
    add_stores([store])
    url = config.get_api_url()

    invalid_store_id = uuid4()
    r = requests.get(f'{url}/stores/{str(invalid_store_id)}/items')
    assert r.status_code == 404
    assert r.json()['message'] == f'Invalid store id {invalid_store_id}'
