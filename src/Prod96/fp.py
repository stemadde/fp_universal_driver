import time
from typing import Tuple, List
from src.fp import AbstractFP, FP as StdFP
from src.Prod96.command import Receipt, Info, Closing, IsReady, Vp, CategoryCmd, HeadersCmd


class FP(AbstractFP):
    STX = b"\x02"
    ETX = b"\x03"
    ACK = b"\x06"
    IDENT = b"0"

    def serialize(self):
        return {
            "serial": self.serial,
            "port": self.port,
            "ip": self.ip,
            "protocol": self.protocol,
            "current_closing": self.current_closing,
            "current_receipt": self.current_receipt,
            "fp_datetime": self.fp_datetime.strftime("%d/%m/%Y %H:%M:%S") if self.fp_datetime else None
        }

    @staticmethod
    def get_cks(string: bytes) -> bytes:
        total = sum(string)
        out = bytes(str(total)[-2:], "ASCII")
        return out

    def wrap_cmd(self, cmd):
        cmd_out: bytes = self.frame_cnt.get_cnt() + self.IDENT + cmd
        cmd_out = self.STX + cmd_out + self.get_cks(cmd_out) + self.ETX
        self.frame_cnt.tick_cnt()
        return cmd_out

    def unwrap_response(self, response: bytes) -> str:
        return response.decode('ascii')[5:-3]

    def __init__(
            self, *args,
            serial='',
            **kwargs
    ):
        if len(args) == 0:
            if 'ip' not in kwargs:
                kwargs['ip'] = '0.0.0.0'
            if 'port' not in kwargs:
                kwargs['port'] = 9100
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
        self.response_serial = ''
        self.sock = None
        self.frame_cnt = self._FrameCounter()
        self.request_fp_data()

    @property
    def max_categories_length(self) -> int:
        return 99

    @property
    def max_headers_length(self) -> int:
        return 6

    @property
    def max_ivas_length(self) -> int:
        return 5

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
        r = response.decode()
        if 'NACK' in r:
            return False, 'Erroneous command syntax'
        elif 'ERR' in r:
            return False, f'Error while performing command: {r}'
        else:
            return True, r

    def push(self):
        self.socket_connect()
        super().push()

    def from_fp(self, std_fp: StdFP):
        pass
        """
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
        """

    def to_fp(self) -> StdFP:
        std_fp = StdFP()
        """
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
        """

    class _FrameCounter:
        def __init__(self) -> None:
            self.frame_counter: int = 0

        def cnt_to_bytes(self, cnt) -> bytes:
            cnt = str(self.frame_counter).zfill(2)
            return cnt.encode(encoding="ISO-8859-15", errors="strict")

        def get_cnt(self) -> bytes:
            return self.cnt_to_bytes(self.frame_counter)

        def tick_cnt(self) -> int:
            current = self.frame_counter

            def rollover(current: int) -> int:
                if current + 1 > 99:
                    current = 0
                else:
                    current += 1
                self.frame_counter = current
                return current

            return rollover(current)

        def reset_cnt(self):
            self.frame_counter = 0

        def set_cnt(self, new_value: int):
            self.frame_counter = new_value

    def is_ready(self) -> bool:
        cmd_list = IsReady().get_cmd()
        for cmd in cmd_list:
            is_successful, response = super().send_cmd(self.wrap_cmd(cmd))
            if not IsReady.is_ready(self.unwrap_response(response)):
                return False
        return True

    def send_cmd(self, cmd: bytes) -> Tuple[bool, bytes]:
        cmd = self.wrap_cmd(cmd)
        is_successful, response = super().send_cmd(cmd)
        return is_successful, response

    def send_cmd_list(self, cmd_list: List[bytes]):
        response_list = []
        error = False
        error_description = ''
        for cmd in cmd_list:
            is_successful, response = self.send_cmd(cmd)
            response_list.append(self.unwrap_response(response))
            if not is_successful:
                error = True
                error_description = response
        return error, error_description, response_list


    def send_receipt(self, product_list: List[dict], payment_list: List[dict]):
        cmd_list = Receipt(product_list, payment_list).get_cmd()
        for cmd in cmd_list:
            is_successful, response = self.send_cmd(cmd)

    def send_closing(self):
        cmd = Closing().get_cmd()
        is_successful, response = self.send_cmd(cmd)
        if is_successful:
            self.current_closing += 1
            self.current_receipt = 1
        while not self.is_ready():
            time.sleep(1)

    def request_fp_data(self):
        cmd_list = Info().get_cmd()
        response_list = []
        for cmd in cmd_list:
            is_successful, response = self.send_cmd(cmd)
            response = self.unwrap_response(response)
            response_list.append(response)

        self.response_serial, self.current_closing, self.current_receipt, self.fp_datetime = Info.parse_response(
            response_list
        )

    def send_vp(self, tech_cf: str, tech_vat: str, lottery_code: str, value1=112, value2=134):
        cmd_list = Vp(
            fp_serial=self.response_serial,
            fp_datetime=self.fp_datetime,
            tech_cf=tech_cf,
            tech_vat=tech_vat,
            current_closing=self.current_closing,
            lottery_code=lottery_code,
            receipt_value_1=value1,
            receipt_value_2=value2,
            perform_first_closing=False,
        ).get_cmd()
        # 0 = Start event
        # 1 = Receipt 1
        # 2 = Receipt 2
        # 3 = Delete Receipt 1
        # 4 = Delete Receipt 2
        # 5 = Closing
        # 6 = End event
        for cmd in cmd_list:
            if isinstance(cmd, bytes):
                is_successful, response = self.send_cmd(cmd)
                while not self.is_ready():
                    time.sleep(1)
            elif isinstance(cmd, list):
                self.send_cmd_list(cmd)

    def send_headers(self):
        cmd = HeadersCmd().send_cmd_bytes(self.headers)
        is_successful, response = self.send_cmd(cmd)
        response = self.unwrap_response(response)

    def get_headers(self):
        cmd = HeadersCmd().get_cmd_bytes_list(self.max_headers_length)
        is_error, error_description, response = self.send_cmd_list(cmd)
        self.headers = HeadersCmd.parse_response(response)

    def send_category(self):
        cmd_list = CategoryCmd().send_cmd_byte_list(self.categories)
        is_error, error, response_list = self.send_cmd_list(cmd_list)
        print()

    def get_category(self):
        cmd = CategoryCmd().get_cmd_byte()
        is_success, response = self.send_cmd(cmd)
        self.categories = CategoryCmd.parse_response(response)
