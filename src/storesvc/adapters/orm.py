from sqlalchemy import (
    Table, MetaData, Column, Integer, String, ForeignKey, CHAR, Float, event
)
from sqlalchemy.orm import mapper, relationship

from storesvc.domain import model

metadata = MetaData()

items = Table(
    'items', metadata,
    Column('id', CHAR(36), primary_key=True),
    Column('name', String(255)),
    Column('price', Float),
    Column('quantity', Integer),
)

stores = Table(
    'stores', metadata,
    Column('id', CHAR(36), primary_key=True),
    Column('name', String(255)),
    Column('version_number', Integer, nullable=False, server_default='0'),
)

store_items_mappings = Table(
    'store_items_mappings', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('store_id', ForeignKey('stores.id')),
    Column('item_id', ForeignKey('items.id')),
)


def start_mappers():
    items_mapper = mapper(model.Item, items)
    mapper(model.Store, stores, properties={
        '_items': relationship(
            items_mapper,
            secondary=store_items_mappings,
            collection_class=list,
        )
    })


@event.listens_for(model.Store, 'load')
def receive_load(store, _):
    store.events = []
