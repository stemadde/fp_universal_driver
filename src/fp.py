import inspect
import logging
from typing import List, Literal
from .category import Category
from .iva import Iva
from .plu import Plu
from .payment import Payment
from .header import Header

logger = logging.getLogger(__name__)


class FP:
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

    def __validate_headers__(self):
        assert len(self.headers) <= 99

    def __validate_ivas__(self):
        assert len(self.ivas) <= 99

    def __validate_plus__(self):
        assert len(self.plus) <= 99999

    def __validate_payments__(self):
        assert len(self.payments) <= 99

    def __validate_categories__(self):
        assert len(self.categories) <= 999

    def __validate__(self):
        # Build a validators var that contains the validator functions for each attribute
        validators = []
        attributes = inspect.getmembers(self, lambda a: not (inspect.isroutine(a)))
        for attr in [a for a in attributes if not (a[0].startswith('__') and a[0].endswith('__'))]:
            validator_function_name = '__validate_' + attr[0] + '__'
            assert hasattr(self, validator_function_name), f'Your class {self} does not have a {attr[0]} validator'
            validators.append(getattr(self, validator_function_name))

        # Run the validations
        for validator in validators:
            validator()
        logger.debug('Validations complete')

    def to_fp(self):
        raise NotImplementedError('to_fp() not implemented')

    def from_fp(self):
        raise NotImplementedError('from_fp() not implemented')

    def connect(self, ip: str, port: int, protocol: Literal['tcp', 'udp']):
        raise NotImplementedError('connect() not implemented')
