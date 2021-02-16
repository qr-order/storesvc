from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
import model
import orm
import provider
import repository
import services

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


@app.route('/stores/<uuid:store_id>/orders', methods=['POST'])
def handle_orders_endpoint(store_id):
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    order_provider = provider.OrderSvcProvider()

    # Todo: Check Authorization
    # ex) store_id in user.store_ids
    order_id = request.json['order_id']
    order_status = request.json['order_status']
    if order_status == model.OrderStatus.APPROVED.value:
        try:
            services.approve_order(order_id, repo, order_provider, session)
        except (model.OutOfStock, model.InvalidOrder) as e:
            return jsonify({'message': str(e)}), 400
        return jsonify({'result': 'success'}), 200
    elif order_status == model.OrderStatus.CANCELED.value:
        # Todo : Publish CancelOrderByStore Event
        pass
    elif order_status == model.OrderStatus.COMPLETED.value:
        # Todo : Publish CompleteOrder Event
        pass
