from abc import ABCMeta
from typing import List
from .validator import validate, is_equal


class AbstractFPGenerics(metaclass=ABCMeta):
    def __init__(self):
        self.__validate__()

    def __validate__(self):
        validate(self)

    def from_fp(self, fp_object: 'AbstractFPObject'):
        raise NotImplementedError('from_fp() not implemented')

    def to_fp(self) -> 'AbstractFPObject':
        raise NotImplementedError('to_fp() not implemented')

    def __eq__(self, other):
        return is_equal(self, other)


class AbstractFPObject(AbstractFPGenerics, metaclass=ABCMeta):
    def push(self):
        raise NotImplementedError('push() not implemented')

    def pull(self):
        raise NotImplementedError('pull() not implemented')


class AbstractFPTable(AbstractFPGenerics, metaclass=ABCMeta):
    @staticmethod
    def push(fp: 'AbstractFPObject', objects: List['AbstractFPTable']):
        raise NotImplementedError('push() not implemented')

    @staticmethod
    def pull(fp: 'AbstractFPObject') -> List['AbstractFPTable']:
        raise NotImplementedError('pull() not implemented')
