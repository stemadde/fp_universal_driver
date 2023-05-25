from typing import Literal, Optional


class Iva:
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
        assert iva_type in ('natura', 'aliquota', 'ventilazione')
        self.natura_code = natura_code
        self.aliquota_value = aliquota_value

    def to_fp(self):
        raise NotImplementedError('to_fp() not implemented')

    def from_fp(self):
        raise NotImplementedError('from_fp() not implemented')

    def __validate_aliquota__(self):
        # Check that the aliquota value is valid (between 0 and 100)
        assert isinstance(self.aliquota_value, float)
        assert 0 < self.aliquota_value < 100

    def __validate__(self):
        if self.iva_type == 'natura':
            assert self.natura_code in ['N1', 'N2', 'N3', 'N4', 'N5', 'N6']
        elif self.iva_type == 'aliquota':
            self.__validate_aliquota__()
