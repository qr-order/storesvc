from dataclasses import dataclass
from storesvc.domain.value import Order


class Event:
    pass


@dataclass
class ApprovedOrder(Event):
    order: Order
