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
            assert len(self.headers) <= self.max_headers_length

    def __validate_ivas__(self):
        if self.max_ivas_length != 0:
            assert len(self.ivas) <= self.max_ivas_length

    def __validate_plus__(self):
        if self.max_plus_length != 0:
            assert len(self.plus) <= self.max_plus_length
        # Check that all plus reference a valid category
        category_ids = [category.id for category in self.categories]
        assert all(plu.category_id in category_ids for plu in self.plus)

    def __validate_payments__(self):
        if self.max_payments_length != 0:
            assert len(self.payments) <= self.max_payments_length

    def __validate_categories__(self):
        if self.max_categories_length != 0:
            assert len(self.categories) <= self.max_categories_length
        # Check that all categories reference a valid iva
        iva_ids = [iva.id for iva in self.ivas]
        assert all(category.iva_id in iva_ids for category in self.categories)

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
