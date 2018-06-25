from abc import ABCMeta, abstractmethod
from builtins import type


class Event(object):
    """
    Event is base class providing an interface for all subsequent
    (inherited) events, that will trigger further events in the
    trading infrastructure.
    """
    __metaclass__ = ABCMeta

    def __init__(self, type: str):
        self._type = type

    @abstractmethod
    def get_as_string(self):
        raise NotImplementedError("Should implement get_as_string()")

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, val: str) -> None:
        self._type = val

