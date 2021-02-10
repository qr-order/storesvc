from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List
from uuid import uuid4


class CannotApprove(Exception):
    pass


class OutOfStock(CannotApprove):
    pass


class InvalidOrder(CannotApprove):
    pass


class OrderStatus(Enum):
    PUBLISHED = 0
    APPROVED = 1
    CANCELED = 2
    COMPLETED = 3


@dataclass(frozen=True)
class Order:
    order_id: str
    order_datetime: datetime
    customer_phone: str
    store_id: uuid4
    item_ids: List[uuid4]
    order_status: OrderStatus


class Item:
    def __init__(self, name: str, price: float, quantity: int, id: uuid4 = None):
        self.id = str(id) if id else str(uuid4())
        self.name = name
        self.price = price
        self.quantity = quantity

    def __eq__(self, other):
        if not isinstance(other, Item):
            return False
        return str(other.id) == str(self.id)

    def __hash__(self):
        return hash(self.id)


class Store:
    def __init__(self, name: str, id: uuid4 = None):
        self.id = str(id) if id else str(uuid4())
        self.name = name
        self._items: List[Item] = list()

    def __eq__(self, other):
        if not isinstance(other, Store):
            return False
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)

    def add_item(self, item: Item) -> uuid4:
        self._items.append(item)
        return item.id

    def delete_item(self, item: Item) -> Item:
        self._items.remove(item)
        return item

    def list_items(self) -> List[Item]:
        return self._items

    def get_item(self, item_id: uuid4) -> Item:
        try:
            item = next(item for item in self._items if item.id == item_id)
            return item
        except StopIteration:
            return None

    def set_item_quantity(self, item_id: uuid4, quantity: int):
        item = self.get_item(item_id)
        if item:
            item.quantity = quantity

    def approve(self, order: Order):
        if self.id != order.store_id:
            raise InvalidOrder(
                f'store id is not matched : store_id of the order({order.order_id}) is {order.store_id} '
                f'but current store_id is {self.id}'
            )

        item_ids = set(order.item_ids)
        ordered_counts = {item_id: order.item_ids.count(item_id) for item_id in item_ids}

        for item_id, ordered_count in ordered_counts.items():
            if item := self.get_item(item_id):
                if item.quantity < ordered_count:
                    raise OutOfStock(
                        f'Out of stock for store_id {self.id}, item {item.id}, order_id {order.order_id}'
                    )
                else:
                    item.quantity -= 1
            else:
                raise InvalidOrder(f'item does not exist : item_id of the order({order.order_id}) is {item_id}')
