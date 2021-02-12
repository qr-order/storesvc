from flask import Flask, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
import orm
import repository

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


@app.route('/stores/<uuid:store_id>/items', methods=['GET'])
def list_items_endpoint(store_id):
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    try:
        store = repo.get(str(store_id))
    except repository.InvalidStoreId as e:
        response = {'message': str(e)}
        status_code = 404
    else:
        items = store.list_items()
        response = {
            'storeId': store.id,
            'storeName': store.name,
            'items': [
                {'id': item.id, 'name': item.name, 'price': item.price, 'quantity': item.quantity} for item in items
            ]
        }
        status_code = 200
    return jsonify(response), status_code
