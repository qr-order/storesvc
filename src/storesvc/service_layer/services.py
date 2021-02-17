from storesvc.adapters.provider import AbstractOrderProvider
from storesvc.service_layer.unit_of_work import AbstractUnitOfWork


def approve_order(order_id: str, uow: AbstractUnitOfWork, provider: AbstractOrderProvider):
    order = provider.get_order(order_id)
    with uow:
        store = uow.stores.get(order.store_id)
        store.approve(order)
        # Todo : Implement Publish PublishedOrder Event Message
        # ex) order = KafkaEventProvider.publish(approved_order)
        #     if fail publish event message then raise Exception
        uow.commit()
