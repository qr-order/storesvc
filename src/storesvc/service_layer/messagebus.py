from typing import List, Dict, Callable, Type

from storesvc.domain import events


def handle(event: events.Event):
    for handler in HANDLERS[type(event)]:
        handler(event)


def publish_approved_order_event_message(event: events.ApprovedOrder):
    # Todo: Integrate with KAFKA Library to publish event message
    pass


HANDLERS = {
    events.ApprovedOrder: [publish_approved_order_event_message],
}  # type: Dict[Type[events.Event], List[Callable]]
