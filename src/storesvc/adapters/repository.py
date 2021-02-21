import abc
from sqlalchemy.orm.exc import NoResultFound
from typing import List, Set

from storesvc.domain import model


class InvalidStoreId(Exception):
    pass


class AbstractRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[model.Store]

    def new(self, store: model.Store):
        self._new(store)
        self.seen.add(store)

    def get(self, id: str) -> model.Store:
        try:
            store = self._get(id)
            self.seen.add(store)
            return store
        except Exception:
            raise

    @abc.abstractmethod
    def _new(self, store: model.Store):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, id: str) -> model.Store:
        raise NotImplementedError

    @abc.abstractmethod
    def _list(self) -> List[model.Store]:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _new(self, store: model.Store):
        self.session.add(store)

    def _get(self, id: str) -> model.Store:
        try:
            return self.session.query(model.Store).filter_by(id=id).one()
        except NoResultFound:
            raise InvalidStoreId(f'Invalid store id {id}')

    def _list(self) -> List[model.Store]:
        return self.session.query(model.Store).all()
