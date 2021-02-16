from repository import AbstractRepository
from provider import AbstractOrderProvider


def approve_order(order_id: str, repo: AbstractRepository, provider: AbstractOrderProvider, session):
    order = provider.get_order(order_id)
    store = repo.get(order.store_id)
    store.approve(order)
    session.commit()
    # Todo : Implement Publish PublishedOrder Event Message
    # ex) order = KafkaEventProvider.publish(approved_order)
