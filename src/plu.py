from abc import ABCMeta
import logging
from .base_fp_object import AbstractFPObject

logger = logging.getLogger(__name__)


class AbstractPlu(AbstractFPObject, metaclass=ABCMeta):
    def __init__(
            self,
            plu_id: int,
            description: str,
            default_price: float,
            category_id: int,
            has_free_price_enabled=True,
            has_discount_enabled=True,
            max_price=999999999.99,
            min_price=0.0,
    ):
        self.id = plu_id
        self.description = description
        self.default_price = default_price
        self.max_price = max_price
        self.min_price = min_price
        self.category_id = category_id
        self.has_free_price_enabled = has_free_price_enabled
        self.has_discount_enabled = has_discount_enabled
        super().__init__()

    @property
    def max_description_length(self) -> int:
        raise NotImplementedError('max_description_length attribute not defined')

    def __validate_max_description_length__(self):
        if len(self.description) > self.max_description_length:
            raise AttributeError(f'Description max length exceeded ({self.max_description_length})')

    def __validate_default_price__(self):
        if self.min_price > self.default_price <= self.max_price:
            raise AttributeError(
                f'Default price {self.default_price} not in range ({self.min_price}, {self.max_price})'
            )


class Plu(AbstractPlu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def max_description_length(self) -> int:
        return 999
