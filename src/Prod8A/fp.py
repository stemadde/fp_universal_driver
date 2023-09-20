import time
from typing import Tuple, List

from src.Prod8A.command import Closing, Info, IsReady, Vp
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
        if 'poses' not in kwargs:
            kwargs['poses'] = []

        super().__init__(*args, **kwargs)
        self.serial = serial  # Matricola
        self.response_serial = ""
        self.sock = None
        self.request_fp_data()

    def unwrap_response(self, response: bytes) -> str:
        return "/".join(response.decode("ascii").split("/")[3:-1])

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

    @property
    def max_poses_length(self) -> int:
        return 99

    def pull(self):
        self.socket_connect()
        super().pull()

    def check_response(self, response: bytes) -> Tuple[bool, str]:
        r = response.decode().split('/')[:2]
        if r[0] == '00' and r[1] == '00':
            return True, ''
        else:
            return False, f'{r[0]}/{r[1]}'

    def send_cmd_list(self, cmd_list: List[bytes]):
        error = False
        error_description = ''
        for cmd in cmd_list:
            is_successful, response = self.send_cmd(cmd)
            if not is_successful:
                error = True
                error_description = response
        return error, error_description

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

    def send_closing(self):
        cmd = Closing().get_cmd()
        is_successful, response = self.send_cmd(cmd)
        if is_successful:
            self.current_closing += 1
            self.current_receipt = 1
        while not self.is_ready():
            time.sleep(1)

    def request_fp_data(self):
        cmd_list = Info().get_cmd_byte_list()
        response_list = []
        for cmd in cmd_list:
            is_successful, response = self.send_cmd(cmd)
            response = self.unwrap_response(response)
            response_list.append(response)

        self.response_serial, self.current_closing, self.current_receipt, self.fp_datetime = Info.parse_response(
            response_list
        )

    def is_ready(self) -> bool:
        cmd_list = IsReady().get_cmd()
        for cmd in cmd_list:
            is_successful, response = super().send_cmd(cmd)
            if not IsReady.is_ready(self.unwrap_response(response)):
                return False
        return True

    def send_vp(self, value1=112, value2=134, lottery_code='UF7KDL1T'):
        cmd_list = Vp(
            fp_serial=self.response_serial,
            fp_datetime=self.fp_datetime,
            current_closing=self.current_closing,
            lottery_code=lottery_code,
            receipt_value_1=value1,
            receipt_value_2=value2,
            perform_first_closing=False,
        ).get_cmd()
        for cmd in cmd_list:
            if isinstance(cmd, bytes):
                is_successful, response = self.send_cmd(cmd)
                while not self.is_ready():
                    time.sleep(1)
            elif isinstance(cmd, list):
                self.send_cmd_list(cmd)
