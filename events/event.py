from abc import ABCMeta, abstractmethod


class Event(object):
    """
    Event is base class providing an interface for all subsequent
    (inherited) events, that will trigger further events in the
    trading infrastructure.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_as_string(self):
        raise NotImplementedError("Should implement get_as_string()")

