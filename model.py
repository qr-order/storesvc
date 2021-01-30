from enum import IntEnum
from typing import List
from uuid import uuid4


class ItemStatus(IntEnum):
    UNAVAILABLE = 0
    AVAILABLE = 1


class Item:
    def __init__(self, name: str, price: float, quantity: int, status: ItemStatus = None, item_id: uuid4 = None):
        self.id = item_id or uuid4()
        self.name = name,
        self.price = price,
        self.quantity = quantity,
        self.status = status or ItemStatus.UNAVAILABLE.value


class Store:
    def __init__(self, name: str, store_id: uuid4 = None):
        self.id = store_id or uuid4()
        self.name = name
        self._items: List[Item] = list()

    def add_items(self, items: List):
        self._items.extend(items)

    def list_items(self):
        return self._items
