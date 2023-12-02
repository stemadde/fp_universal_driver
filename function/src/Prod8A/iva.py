from typing import List
from typing import TYPE_CHECKING
from src.iva import AbstractIva, Iva as StdIva

if TYPE_CHECKING:
    from src.Prod8A.fp import FP


class Iva(AbstractIva):
    def __init__(
            self,
            *args,
            natura_code=0,
            **kwargs
    ):
        if len(args) == 0:
            if 'iva_id' not in kwargs:
                kwargs['iva_id'] = 1
            if 'iva_type' not in kwargs:
                kwargs['iva_type'] = 'aliquota'
            if 'aliquota_value' not in kwargs:
                kwargs['aliquota_value'] = 22.0
        super().__init__(*args, **kwargs, natura_code=natura_code)
        if self.iva_type == 'ventilazione':
            self.natura_code = 6

    @property
    def min_aliquota_value(self) -> float:
        return 0.0

    @property
    def max_aliquota_value(self) -> float:
        return 100.0

    def __validate_id__(self):
        if not 1 <= self.id <= 12:
            raise AttributeError(f'Invalid iva id {self.id}')

    def __validate_natura__(self):
        if self.iva_type == 'natura':
            if not isinstance(self.natura_code, int):
                raise AttributeError(f'Invalid natura code type {self.natura_code}')
            if self.natura_code not in [0, 1, 2, 3, 4, 5]:
                raise AttributeError(f'Invalid natura code {self.natura_code}')

    def __validate_ventilazione__(self):
        if self.iva_type == 'ventilazione':
            if self.natura_code != 6:
                raise AttributeError(f'Attribute natura_code must be set to 6 for ventilazione iva type')

    def to_fp(self) -> StdIva:
        iva_codes_map = {
            0: "N1",
            1: "N2",
            2: "N3",
            3: "N4",
            4: "N5",
            5: "N6",
            6: "",
        }
        iva = StdIva(
            iva_id=self.id,
            iva_type=self.iva_type,
            aliquota_value=self.aliquota_value,
            natura_code=iva_codes_map[self.natura_code],
            ateco_code=self.ateco_code,
        )
        return iva

    def from_fp(self, iva: StdIva):
        iva_codes_map = {
            "N1": 0,
            "N2": 1,
            "N3": 2,
            "N4": 3,
            "N5": 4,
            "N6": 5,
        }
        self.id = iva.id
        self.iva_type = iva.iva_type
        self.aliquota_value = iva.aliquota_value
        if iva.iva_type == 'natura':
            self.natura_code = iva_codes_map[iva.natura_code]
        elif iva.iva_type == 'ventilazione':
            self.natura_code = 6
        self.ateco_code = iva.ateco_code
        return

    def convert_to_cmd(self) -> bytes:
        if self.iva_type == 'aliquota':
            # Convert aliquota_value to bytes
            return bytes(int(self.aliquota_value * 100))
        elif self.iva_type == 'natura':
            return bytes(self.natura_code)

    @staticmethod
    def push(fp: 'FP', objects: List['Iva']):
        pass

    @staticmethod
    def pull(fp: 'FP') -> List['Iva']:
        # Iva
        code = b'e/'
        return_list = []
        is_successful, response = fp.send_cmd(code)
        if is_successful:
            # Convert response bytes to ivas
            response = response.decode().split('/')[2:-1]  # Exclude printer status and checksum
            for i in range(0, fp.max_ivas_length):
                aliquota = float(response[i + 1])
                natura = int(response[i + 1 + 12])
                ateco = int(response[i + 1 + 24])
                iva_type = 'aliquota'
                if natura != 0:
                    if natura != 6:
                        iva_type = 'natura'
                    else:
                        iva_type = 'ventilazione'
                return_list.append(Iva(
                    iva_id=i + 1,
                    iva_type=iva_type,
                    aliquota_value=aliquota,
                    natura_code=natura,
                    ateco_code=ateco,
                ))
        else:
            raise Exception('Error while reading ivas from printer')
        return return_list
