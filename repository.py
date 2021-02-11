import abc
from sqlalchemy.orm.exc import NoResultFound
from uuid import uuid4

import model

class InvalidStoreId(Exception):
    pass


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def new(self, store: model.Store):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, id: uuid4) -> model.Store:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def new(self, store: model.Store):
        self.session.add(store)

    def get(self, id: str) -> model.Store:
        try:
            return self.session.query(model.Store).filter_by(id=id).one()
        except NoResultFound:
            raise InvalidStoreId(f'Invalid store id {id}')

    def list(self):
        return self.session.query(model.Store).all()
