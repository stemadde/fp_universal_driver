from typing import List
from src.Prod8A.fp import FP
from src.pos import AbstractPos


class Pos(AbstractPos):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def max_description_length(self) -> int:
        return 20

    def to_fp(self) -> 'Pos':
        pass

    def from_fp(self, pos: 'Pos'):
        pass

    @staticmethod
    def push(fp: FP, objects: List['Pos']):
        pass

    @staticmethod
    def pull(fp: FP) -> List['Pos']:
        pass
