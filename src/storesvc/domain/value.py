from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List


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
    store_id: str
    item_ids: List[str]
    order_status: OrderStatus