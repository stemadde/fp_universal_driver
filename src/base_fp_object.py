from abc import ABCMeta
from .validator import validate, is_equal


class AbstractFPObject(metaclass=ABCMeta):
    def __init__(self):
        self.__validate__()

    def from_fp(self, fp_object: 'AbstractFPObject'):
        raise NotImplementedError('from_fp() not implemented')

    def to_fp(self) -> 'AbstractFPObject':
        raise NotImplementedError('to_fp() not implemented')

    def push(self):
        raise NotImplementedError('push() not implemented')

    def pull(self):
        raise NotImplementedError('pull() not implemented')

    def __validate__(self):
        validate(self)

    def __eq__(self, other):
        return is_equal(self, other)
