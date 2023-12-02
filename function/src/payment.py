from abc import ABCMeta
from typing import Literal, Optional
from .base_fp_object import AbstractFPTable
import logging

logger = logging.getLogger(__name__)


class AbstractPayment(AbstractFPTable, metaclass=ABCMeta):
    def __init__(
            self,
            payment_id: int,
            description: str,
            payment_type: Literal['riscosso', 'non_riscosso_b_s', 'non_riscosso_fatture', 'ticket', 'sconto_a_pagare'],
            payment_subtype: Optional[Literal['contanti', 'elettronico']],
            drawer_open=True,  # Apertura cassetto
            require_value=False,  # Importo obbligatorio
            pos_id=0,
    ):
        self.id = payment_id
        self.description = description
        if payment_type not in ['riscosso', 'non_riscosso_b_s', 'non_riscosso_fatture', 'ticket', 'sconto_a_pagare']:
            raise AttributeError(
                f'payment_type must be one of "riscosso", "non_riscosso_b_s", "non_riscosso_fatture", '
                f'"ticket", "sconto_a_pagare"'
            )
        self.payment_type = payment_type
        if payment_type == 'riscosso':
            if payment_subtype not in ['contanti', 'elettronico']:
                raise AttributeError(
                    f'payment_subtype must be one of "contanti", "elettronico" for payment_type "riscosso"'
                )
        self.payment_subtype = payment_subtype
        self.drawer_open = drawer_open
        self.require_value = require_value
        self.pos_id = pos_id
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

    def __validate_pos_id__(self):
        if self.pos_id < 0:
            raise AttributeError(f'pos_id must be 0 [disabled] or greater')
        if self.pos_id > 0 and (self.payment_type != 'riscosso' or self.payment_subtype != 'elettronico'):
            raise AttributeError(f'pos_id can only be set for payments of type "riscosso" with subtype "elettronico"')

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key == 'description':
            self.__validate_max_description_length__()
        if key in ['pos_id', 'payment_type', 'payment_subtype']:
            if hasattr(self, 'pos_id') and hasattr(self, 'payment_type') and hasattr(self, 'payment_subtype'):
                self.__validate_pos_id__()


class Payment(AbstractPayment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def max_description_length(self) -> int:
        return 9999
