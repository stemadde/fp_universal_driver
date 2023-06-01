from typing import Tuple, List
from src.Prod8A.iva import Iva
from src.Prod8A.payment import Payment
from src.Prod8A.header import Header
from src.Prod8A.category import Category
from src.Prod8A.plu import Plu
from src.fp import AbstractFP, FP as StdFP


class FP(AbstractFP):
    def __init__(
            self, *args,
            serial='',
            **kwargs
    ):
        if len(args) == 0:
            if 'ip' not in kwargs:
                kwargs['ip'] = '0.0.0.0'
            if 'port' not in kwargs:
                kwargs['port'] = 9101
        if 'ivas' not in kwargs:
            kwargs['ivas'] = []
        if 'payments' not in kwargs:
            kwargs['payments'] = []
        if 'headers' not in kwargs:
            kwargs['headers'] = []
        if 'categories' not in kwargs:
            kwargs['categories'] = []
        if 'plus' not in kwargs:
            kwargs['plus'] = []

        super().__init__(*args, **kwargs)
        self.serial = serial  # Matricola
        self.sock = None

    @property
    def max_categories_length(self) -> int:
        return 99

    @property
    def max_headers_length(self) -> int:
        return 8

    @property
    def max_ivas_length(self) -> int:
        return 12

    @property
    def max_plus_length(self) -> int:
        return 9999

    @property
    def max_payments_length(self) -> int:
        return 99

    def pull(self):
        self.socket_connect()
        super().pull()

    def pull_ivas(self):
        # Iva
        code = b'e/'
        is_successful, response = self.send_cmd(code)
        if is_successful:
            # Convert response bytes to ivas
            response = response.decode().split('/')[2:-1]  # Exclude printer status and checksum
            for i in range(0, self.max_ivas_length):
                aliquota = float(response[i + 1])
                natura = int(response[i + 1 + 12])
                ateco = int(response[i + 1 + 24])
                iva_type = 'aliquota'
                if natura != 0:
                    if natura != 6:
                        iva_type = 'natura'
                    else:
                        iva_type = 'ventilazione'
                self.ivas.append(Iva(
                    iva_id=i + 1,
                    iva_type=iva_type,
                    aliquota_value=aliquota,
                    natura_code=natura,
                    ateco_code=ateco,
                ))
        else:
            raise Exception('Error while reading ivas from printer')

    def pull_payments(self):
        code = b'{/'
        for i in range(0, self.max_payments_length - 1):
            is_successful, response = self.send_cmd(code + bytes([i + 1]))
            if is_successful:
                # Convert response bytes to ivas
                response = response.decode().split('/')[2:-1]  # Exclude printer status and checksum
                self.payments.append(Payment(
                    payment_id=i + 1,
                    description=response[0],
                    payment_type=response[4],
                ))

    def check_response(self, response: bytes) -> Tuple[bool, str]:
        r = response.decode().split('/')[:2]
        if r[0] == '00' and r[1] == '00':
            return True, ''
        else:
            return False, f'{r[0]}/{r[1]}'

    def push(self):
        self.socket_connect()
        super().push()

    def from_fp(self, std_fp: StdFP):
        for std_iva in std_fp.ivas:
            self.ivas.append(Iva().from_fp(std_iva))
        for std_payment in std_fp.payments:
            self.payments.append(Payment().from_fp(std_payment))
        for std_header in std_fp.headers:
            self.headers.append(Header().from_fp(std_header))
        for std_category in std_fp.categories:
            self.categories.append(Category().from_fp(std_category))
        for std_plu in std_fp.plus:
            self.plus.append(Plu().from_fp(std_plu))

    def to_fp(self) -> StdFP:
        std_fp = StdFP()
        for iva in self.ivas:
            std_fp.ivas.append(iva.to_fp())
        for payment in self.payments:
            std_fp.payments.append(payment.to_fp())
        for header in self.headers:
            std_fp.headers.append(header.to_fp())
        for category in self.categories:
            std_fp.categories.append(category.to_fp())
        for plu in self.plus:
            std_fp.plus.append(plu.to_fp())
        return std_fp
