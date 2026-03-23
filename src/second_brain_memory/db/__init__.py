from .connection import ConnectionMixin
from .memories import MemoriesMixin
from .sessions import SessionMixin
from .stats import StatsMixin


class MemoryDB(ConnectionMixin, MemoriesMixin, SessionMixin, StatsMixin):
    pass
