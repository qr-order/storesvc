import abc
import config
import datetime
import requests
from typing import List

import model


class InvalidOrderId(Exception):
    pass


class AbstractOrderProvider(abc.ABC):
    @abc.abstractmethod
    def get_order(self, order_id: str) -> model.Order:
        raise NotImplementedError

    @abc.abstractmethod
    def list_orders(self, order_id: str) -> List[model.Order]:
        raise NotImplementedError


class OrderSvcProvider(AbstractOrderProvider):
    def __init__(self):
        self._url = config.get_order_svc_url()

    def get_order(self, order_id: str) -> model.Order:
        r = requests.get(url=f'{self._url}/api/orders/{order_id}')
        order = model.Order(
            order_id=order_id,
            order_datetime=datetime.datetime(r['orderDate']),
            customer_phone=r['customerPhoneNumber'],
            store_id=r['storeId'],
            item_ids=r['itemIds'],
            order_status=r['orderStatus'],
        )
        return order

    def list_orders(self, store_id: str) -> List[model.Order]:
        r = requests.get(url=f'{self._url}/api/orders/stores/{store_id}')
        orders = []
        for order in r['orders']:
            orders.append(
                model.Order(
                    order_id=order['id'],
                    order_datetime=datetime.datetime(order['orderDate']),
                    customer_phone=order['customerPhoneNumber'],
                    store_id=order['storeId'],
                    item_ids=order['itemIds'],
                    order_status=order['orderStatus'],
                )
            )
        return orders
