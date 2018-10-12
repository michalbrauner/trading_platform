from abc import ABCMeta, abstractmethod


class Event(object):
    __metaclass__ = ABCMeta

    def __init__(self, event_type: str, symbol: str):
        self._type = event_type
        self._symbol = symbol

    @abstractmethod
    def get_as_string(self):
        raise NotImplementedError("Should implement get_as_string()")

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, val: str) -> None:
        self._type = val

    @property
    def symbol(self) -> str:
        return self._symbol

