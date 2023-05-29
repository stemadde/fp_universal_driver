from abc import ABCMeta
import logging
from .validator import validate

logger = logging.getLogger(__name__)


class AbstractPlu(metaclass=ABCMeta):
    def __init__(
            self,
            plu_id: int,
            description: str,
            default_price: float,
            max_price: float,
            min_price: float,
            category_id: int,
            has_free_price_enabled=True,
            has_discount_enabled=True,
    ):
        self.id = plu_id
        self.description = description
        self.default_price = default_price
        self.max_price = max_price
        self.min_price = min_price
        self.category_id = category_id
        self.has_free_price_enabled = has_free_price_enabled
        self.has_discount_enabled = has_discount_enabled

    def to_fp(self):
        raise NotImplementedError('to_fp() not implemented')

    def from_fp(self):
        raise NotImplementedError('from_fp() not implemented')

    @property
    def max_description_length(self) -> int:
        raise NotImplementedError('max_description_length attribute not defined')

    def __validate_max_description_length__(self):
        assert len(self.description) <= self.max_description_length, \
            f'Description max length exceeded ({self.max_description_length})'

    def __validate_default_price__(self):
        assert self.min_price <= self.default_price <= self.max_price, \
            f'Default price {self.default_price} not in range ({self.min_price}, {self.max_price})'

    def __validate__(self):
        validate(self)
        logger.debug(f'Validations for plu {self} complete')


class Plu(AbstractPlu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def max_description_length(self) -> int:
        return 999
