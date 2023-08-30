from typing import Tuple, List
from src.fp import AbstractFP, FP as StdFP
from src.Prod96.command import Receipt


class FP(AbstractFP):
    STX = b"\x02"
    ETX = b"\x03"
    ACK = b"\x06"
    IDENT = b"0"

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
        self.sock = None
        self.frame_cnt = self._FrameCounter()

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

    def send_cmd(self, cmd: bytes) -> Tuple[bool, bytes]:
        cmd = self.wrap_cmd(cmd)
        return super().send_cmd(cmd)

    def send_receipt(self, product_list: List[dict], payment_list: List[dict]):
        cmd_list = Receipt(product_list, payment_list).get_cmd()
        for cmd in cmd_list:
            self.send_cmd(cmd)
