import abc
import datetime
import requests
from typing import List

import storesvc.domain.value
from storesvc.domain import model
from storesvc import config


class InvalidOrderId(Exception):
    pass


class AbstractOrderProvider(abc.ABC):
    @abc.abstractmethod
    def get_order(self, order_id: str) -> storesvc.domain.value.Order:
        raise NotImplementedError

    @abc.abstractmethod
    def list_orders(self, order_id: str) -> List[storesvc.domain.value.Order]:
        raise NotImplementedError


class OrderSvcProvider(AbstractOrderProvider):
    def __init__(self):
        self._url = config.get_order_svc_url()

    def get_order(self, order_id: str) -> storesvc.domain.value.Order:
        r = requests.get(url=f'{self._url}/api/orders/{order_id}')
        order = self.to_domain(r)
        return order

    def list_orders(self, store_id: str) -> List[storesvc.domain.value.Order]:
        r = requests.get(url=f'{self._url}/api/orders/stores/{store_id}')
        orders = []
        for order in r['orders']:
            o = self.to_domain(order)
            orders.append(o)
        return orders

    @staticmethod
    def to_domain(order: dict):
        return storesvc.domain.value.Order(
            order_id=order['id'],
            order_datetime=datetime.datetime(order['orderDate']),
            customer_phone=order['customerPhoneNumber'],
            store_id=order['storeId'],
            item_ids=order['itemIds'],
            order_status=order['orderStatus'],
        )
