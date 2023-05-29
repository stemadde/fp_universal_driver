from abc import ABCMeta
from .validator import validate
import logging
from typing import List, Literal
from .category import Category
from .iva import Iva
from .plu import Plu
from .payment import Payment
from .header import Header

logger = logging.getLogger(__name__)


class AbstractFP(metaclass=ABCMeta):
    """
    Core class for the fp_universal_driver
    Every producer subclasses this FP class, providing functions to translate it's own tables
    to the FPs one and vice versa.
    """
    def __init__(
            self,
            categories: List[Category],
            plus: List[Plu],
            ivas: List[Iva],
            payments: List[Payment],
            headers: List[Header],
    ):
        self.categories = categories
        self.plus = plus
        self.ivas = ivas
        self.payments = payments
        self.headers = headers
        # Run class validations
        self.__validate__()

    @property
    def max_headers_length(self) -> int:
        raise NotImplementedError('max_headers_length attribute not defined')

    @property
    def max_ivas_length(self) -> int:
        raise NotImplementedError('max_ivas_length attribute not defined')

    @property
    def max_plus_length(self) -> int:
        raise NotImplementedError('max_plus_length attribute not defined')

    @property
    def max_payments_length(self) -> int:
        raise NotImplementedError('max_payments_length attribute not defined')

    @property
    def max_categories_length(self) -> int:
        raise NotImplementedError('max_categories_length attribute not defined')

    def __validate_headers__(self):
        if self.max_headers_length != 0:
            if len(self.headers) > self.max_headers_length:
                raise AttributeError(f'Headers max length exceeded ({self.max_headers_length})')

    def __validate_ivas__(self):
        if self.max_ivas_length != 0:
            if len(self.ivas) > self.max_ivas_length:
                raise AttributeError(f'Ivas max length exceeded ({self.max_ivas_length})')

    def __validate_plus__(self):
        if self.max_plus_length != 0:
            if len(self.plus) > self.max_plus_length:
                raise AttributeError(f'Plus max length exceeded ({self.max_plus_length})')
        # Check that all plus reference a valid category
        category_ids = [category.id for category in self.categories]
        for plu in self.plus:
            if plu.category_id not in category_ids:
                raise AttributeError(f'Plu {plu} references a non existent category: {plu.category_id}')

    def __validate_payments__(self):
        if self.max_payments_length != 0:
            if len(self.payments) > self.max_payments_length:
                raise AttributeError(f'Payments max length exceeded ({self.max_payments_length})')

    def __validate_categories__(self):
        if self.max_categories_length != 0:
            if len(self.categories) > self.max_categories_length:
                raise AttributeError(f'Categories max length exceeded ({self.max_categories_length})')
        # Check that all categories reference a valid iva
        iva_ids = [iva.id for iva in self.ivas]
        for category in self.categories:
            if category.iva_id not in iva_ids:
                raise AttributeError(f'Category {category} references a non existent iva: {category.iva_id}')

    def __validate__(self):
        validate(self)
        logger.debug(f'Validations for fp {self} complete')

    def to_fp(self):
        raise NotImplementedError('to_fp() not implemented')

    def from_fp(self):
        raise NotImplementedError('from_fp() not implemented')

    def connect(self, ip: str, port: int, protocol: Literal['tcp', 'udp']):
        raise NotImplementedError('connect() not implemented')


class FP(AbstractFP):
    """
    This class is used to perform tests of the Abstract Parent.
    No real use should be done from this class.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def max_headers_length(self) -> int:
        return 0

    @property
    def max_ivas_length(self) -> int:
        return 0

    @property
    def max_plus_length(self) -> int:
        return 0

    @property
    def max_payments_length(self) -> int:
        return 0

    @property
    def max_categories_length(self) -> int:
        return 0
