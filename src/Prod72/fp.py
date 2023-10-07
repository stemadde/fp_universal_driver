import socket
import time
from typing import Tuple, List

from src.Prod72.command import Info, Closing, Receipt
from src.fp import AbstractFP, FP as StdFP, logger


class FP(AbstractFP):
    STX = b"\x02"
    ADDS = b"01"
    ETX = b"\x03"
    ACK = b"\x06"
    NACK = b"\x15"
    PROT_ID = b"N"
    IDENT = b"0"
    MAX_WAIT = 3

    @staticmethod
    def get_cks(cmd: bytes) -> bytes:
        checksum = 0
        for byte in cmd:
            checksum ^= byte
        cks_hex = format(checksum, '02x')
        return cks_hex.encode('ascii')

    def wrap_cmd(self, cmd):
        cmd_out: bytes = self.STX + self.ADDS + str(len(cmd)).zfill(3).encode("ascii") + self.PROT_ID + cmd + self.frame_cnt.get_cnt()
        cmd_out = cmd_out + self.get_cks(cmd_out) + self.ETX
        self.frame_cnt.tick_cnt()
        return cmd_out

    def unwrap_response(self, response: bytes) -> str:
        if response == self.ACK:
            return ""
        response = response.decode('ascii')
        pre = self.ACK + self.STX + self.ADDS
        pre = len(pre.decode('ascii'))
        data_len = int(response[pre:pre+3])
        response = response[pre+3+len(self.PROT_ID):pre+3+len(self.PROT_ID)+data_len]
        return response

    def check_error(self, is_successful: bool, response: str) -> Tuple[bool, str]:
        if response.startswith("E"):
            is_successful = False
            response = response[2:]
        else:
            response = response[1:]
        return is_successful, response

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
        return 9

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

        def cnt_to_bytes(self) -> bytes:
            cnt = str(self.frame_counter)
            return cnt.encode(encoding="ISO-8859-15", errors="strict")

        def get_cnt(self) -> bytes:
            return self.cnt_to_bytes()

        def tick_cnt(self) -> int:
            current = self.frame_counter

            def rollover(current: int) -> int:
                if current + 1 > 9:
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
        """cmd_list = IsReady().get_cmd()
        for cmd in cmd_list:
            is_successful, response = super().send_cmd(self.wrap_cmd(cmd))
            if not IsReady.is_ready(self.unwrap_response(response)):
                return False
        return True"""
        pass

    def send_cmd(self, cmd: bytes) -> Tuple[bool, bytes]:
        def inner_send_cmd(cmd):
            try:
                self.socket_connect()
                assert isinstance(self.sock, socket.socket)
                for i in range(self.MAX_TRIES):
                    self.sock.sendall(cmd)
                    self.sock.settimeout(30.0)
                    time.sleep(0.180)
                    # Get the response
                    response = b''
                    timer = 0
                    while True:
                        response += self.sock.recv(1024)
                        if self.ETX in response:
                            break
                        time.sleep(0.200)
                        timer += 0.200
                        if timer > self.MAX_WAIT:
                            logger.warning(f"Error while sending command to printer: no ETX")
                            return False, response
                    has_succeeded, error = self.check_response(response)
                    if has_succeeded:
                        return True, response
                    else:
                        logger.warning(f"Error while sending command to printer: {error}")
                        time.sleep(self.TRY_DELAY)  # Wait half a second to allow printer buffer to empy
                return False, 'Numero massimo di tentativi raggiunto'.encode()
            except socket.timeout as e:
                logger.error(str(e))
                return False, str(e).encode()
            except BaseException as e:
                logger.error(str(e))
                return False, str(e).encode()

        cmd = self.wrap_cmd(cmd)
        is_successful, response = inner_send_cmd(cmd)
        return is_successful, response

    def send_cmd_list(self, cmd_list: List[bytes]):
        error = False
        error_description = ''
        for cmd in cmd_list:
            is_successful, response = self.send_cmd(cmd)
            if not is_successful:
                error = True
                error_description = response
        return error, error_description

    def send_receipt(self, product_list: List[dict], payment_list: List[dict]):
        cmd_list = Receipt(product_list, payment_list).get_cmd()
        for cmd in cmd_list:
            is_successful, response = self.send_cmd(cmd)

    def send_closing(self):
        cmd_list = Closing().get_cmd_byte_list()
        response_list = []
        for cmd in cmd_list:
            is_successful, response = self.send_cmd(cmd)
            response = self.unwrap_response(response)
            is_successful, response = self.check_error(is_successful, response)
            response_list.append(response)
        return response_list

    def request_fp_data(self):
        cmd_list = Info().get_cmd_byte_list()
        response_list = []
        for cmd in cmd_list:
            is_successful, response = self.send_cmd(cmd)
            response = self.unwrap_response(response)
            is_successful, response = self.check_error(is_successful, response)
            response_list.append(response)

        self.response_serial, self.current_closing, self.current_receipt, self.fp_datetime = Info.parse_response(
            response_list
        )

    def send_vp(self, tech_cf: str, tech_vat: str, lottery_code: str, value1=112, value2=134):
        pass
