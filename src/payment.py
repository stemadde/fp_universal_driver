from abc import ABCMeta
from typing import Literal, Optional
from .validator import validate, is_equal
import logging

logger = logging.getLogger(__name__)


class AbstractPayment(metaclass=ABCMeta):
    def __init__(
            self,
            payment_id: int,
            description: str,
            payment_type: Literal['riscosso', 'non_riscosso_b_s', 'non_riscosso_fatture', 'ticket', 'sconto_a_pagare'],
            payment_subtype: Optional[Literal['contanti', 'elettronico']],
            drawer_open=True,  # Apertura cassetto
            require_value=False,  # Importo obbligatorio
    ):
        self.id = payment_id
        self.description = description
        assert payment_type in ['riscosso', 'non_riscosso_b_s', 'non_riscosso_fatture', 'ticket', 'sconto_a_pagare']
        self.payment_type = payment_type
        if payment_type == 'riscosso':
            assert payment_subtype
            assert payment_subtype in ['contanti', 'elettronico']
        self.payment_type_subtype = payment_subtype
        self.drawer_open = drawer_open
        self.require_value = require_value
        self.__validate__()

    def to_fp(self) -> 'Payment':
        raise NotImplementedError('to_fp() not implemented')

    def from_fp(self, payment: 'Payment'):
        raise NotImplementedError('from_fp() not implemented')

    @property
    def max_description_length(self) -> int:
        """
        When inheriting overwrite this with the max number of chars supported by the protocol
        """
        raise NotImplementedError('max_description_length attribute not defined')

    def __validate_max_description_length__(self):
        assert len(self.description) <= self.max_description_length, \
            f'Description max length exceeded ({self.max_description_length})'

    def __validate__(self):
        """
        Performs validations such as checking that the description provided does not exceed the description max length
        """
        validate(self)
        logger.debug(f'Validations for Payment {self} complete')

    def __eq__(self, other):
        return is_equal(self, other)


class Payment(AbstractPayment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def max_description_length(self) -> int:
        return 9999
