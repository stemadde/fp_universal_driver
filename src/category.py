from typing import Optional
import logging
from .validator import validate
from abc import ABCMeta

logger = logging.getLogger(__name__)


class AbstractCategory(metaclass=ABCMeta):
    def __init__(
            self,
            category_id: int,
            description: str,
            default_price: Optional[float],
            iva_id: int,
            max_price=999999999.99,
            min_price=0.0,
    ):
        self.id = category_id
        self.description = description
        self.default_price = default_price
        self.max_price = max_price
        self.min_price = min_price
        self.iva_id = iva_id

    def to_fp(self) -> 'Category':
        raise NotImplementedError('to_fp() not implemented')

    def from_fp(self, category: 'Category'):
        raise NotImplementedError('from_fp() not implemented')

    @property
    def max_description_length(self) -> int:
        """
        When inheriting overwrite this with the max number of chars supported by the protocol
        """
        raise NotImplementedError('max_description_length attribute not defined')

    def __validate_max_description_length__(self):
        if len(self.description) > self.max_description_length:
            raise AttributeError(f'Description max length exceeded ({self.max_description_length})')

    def __validate__(self):
        validate(self)
        logger.debug(f'Validations for category {self} complete')

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key == 'description':
            self.__validate_max_description_length__()


class Category(AbstractCategory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def max_description_length(self) -> int:
        return 999
