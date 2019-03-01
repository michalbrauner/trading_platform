from abc import ABCMeta, abstractmethod

from strategies.patterns.pattern_resolving_result import PatternResolvingResult


class Pattern(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def resolve(self) -> PatternResolvingResult:
        raise NotImplementedError("Should implement is_valid()")

