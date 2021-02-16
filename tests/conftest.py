import pytest
import time
import requests
from pathlib import Path
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, clear_mappers

from storesvc import config
from storesvc.domain import model
from storesvc.adapters.orm import metadata, start_mappers


@pytest.fixture
def in_memory_db():
    engine = create_engine('sqlite:///:memory:')
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()


def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    pytest.fail('API never came up')


def wait_for_postgres_to_come_up(engine):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)
    pytest.fail('Postgres never came up')


@pytest.fixture(scope='session')
def postgres_db():
    engine = create_engine(config.get_postgres_uri())
    wait_for_postgres_to_come_up(engine)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def postgres_session(postgres_db):
    start_mappers()
    yield sessionmaker(bind=postgres_db)()
    clear_mappers()


@pytest.fixture
def add_stores(postgres_session):
    stores_added = list()

    def _add_stores(stores: List[model.Store]):
        for store in stores:
            postgres_session.add(store)
            stores_added.append(store)
        postgres_session.commit()

    yield _add_stores

    for store in stores_added:
        for item in store.list_items():
            postgres_session.delete(item)
        postgres_session.delete(store)
    postgres_session.commit()

@pytest.fixture
def restart_api():
    (Path(__file__).parent / 'flask_app.py').touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()

