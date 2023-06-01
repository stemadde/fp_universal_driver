from abc import ABCMeta
from typing import Literal, List
from .base_fp_object import AbstractFPTable
import logging

logger = logging.getLogger(__name__)


class AbstractPos(AbstractFPTable, metaclass=ABCMeta):
    def __init__(
            self,
            pos_id: int,
            description: str,
            ip: str,
            port: int,
            protocol: Literal['ingenico', 'other'],
    ):
        self.id = pos_id
        self.description = description
        self.ip = ip
        self.port = port
        self.protocol = protocol
        super().__init__()

    @property
    def max_description_length(self) -> int:
        raise NotImplementedError('max_description_length attribute not defined')

    def __validate_max_description_length__(self):
        if len(self.description) > self.max_description_length:
            raise AttributeError(f'Description max length exceeded ({self.max_description_length})')

    @staticmethod
    def push(fp, objects: List['Pos']):
        raise NotImplementedError('push() not implemented')

    @staticmethod
    def pull(fp) -> List['Pos']:
        raise NotImplementedError('pull() not implemented')


class Pos(AbstractPos):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def max_description_length(self) -> int:
        return 999

