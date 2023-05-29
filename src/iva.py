from abc import ABCMeta
from typing import Literal, Optional
import logging
from .validator import validate

logger = logging.getLogger(__name__)


class AbstractIva(metaclass=ABCMeta):
    def __init__(
            self,
            iva_id: int,
            iva_type: Literal['natura', 'aliquota', 'ventilazione'],
            aliquota_value: Optional[float],
            natura_code: Optional[Literal['N1', 'N2', 'N3', 'N4', 'N5', 'N6']]
    ):
        self.id = iva_id
        self.iva_type = iva_type
        # Check that iva type is valid
        self.natura_code = natura_code
        self.aliquota_value = aliquota_value
        self.__validate__()

    def to_fp(self):
        raise NotImplementedError('to_fp() not implemented')

    def from_fp(self):
        raise NotImplementedError('from_fp() not implemented')

    @property
    def min_aliquota_value(self) -> float:
        raise NotImplementedError('min_aliquota_value attribute not defined')

    @property
    def max_aliquota_value(self) -> float:
        raise NotImplementedError('max_aliquota_value attribute not defined')

    def __validate_iva_type__(self):
        if self.iva_type not in ('natura', 'aliquota', 'ventilazione'):
            raise AttributeError(f'Invalid iva type {self.iva_type}')
        if self.iva_type == 'aliquota':
            self.__inner_validate_aliquota__()
        elif self.iva_type == 'natura':
            self.__inner_validate_natura__()

    def __inner_validate_aliquota__(self):
        if not isinstance(self.aliquota_value, float):
            raise AttributeError(f'Invalid aliquota value type {self.aliquota_value}')
        if not self.min_aliquota_value < self.aliquota_value < self.max_aliquota_value:
            raise AttributeError(f'Invalid aliquota value {self.aliquota_value}')

    def __inner_validate_natura__(self):
        if not isinstance(self.natura_code, str):
            raise AttributeError(f'Invalid natura code type {self.natura_code}')
        if self.natura_code not in ['N1', 'N2', 'N3', 'N4', 'N5', 'N6']:
            raise AttributeError(f'Invalid natura code {self.natura_code}')

    def __validate__(self):
        validate(self)
        logger.debug(f'Validations for iva {self} complete')

    def __setattr__(self, key, value):
        if key == 'iva_type':
            self.__validate_iva_type__()
        elif key == 'aliquota_value':
            self.__inner_validate_aliquota__()
        elif key == 'natura_code':
            self.__inner_validate_natura__()
        super().__setattr__(key, value)


class Iva(AbstractIva):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def min_aliquota_value(self) -> float:
        return 0.0

    @property
    def max_aliquota_value(self) -> float:
        return 100.0
