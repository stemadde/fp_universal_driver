from typing import Optional
import logging
from .base_fp_object import AbstractFPTable
from abc import ABCMeta

logger = logging.getLogger(__name__)


class AbstractCategory(AbstractFPTable, metaclass=ABCMeta):
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
        super().__init__()

    @property
    def max_description_length(self) -> int:
        """
        When inheriting overwrite this with the max number of chars supported by the protocol
        """
        raise NotImplementedError('max_description_length attribute not defined')

    def __validate_max_description_length__(self):
        if len(self.description) > self.max_description_length:
            raise AttributeError(f'Description max length exceeded ({self.max_description_length})')

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
