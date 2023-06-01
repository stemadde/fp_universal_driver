import socket
import time
from abc import ABCMeta
from .validator import validate, is_equal
import logging
from typing import List, Literal, Tuple
from .category import Category
from .iva import Iva
from .plu import Plu
from .payment import Payment
from .header import Header

logger = logging.getLogger(__name__)


class AbstractFP(metaclass=ABCMeta):
    """
    Core class for the fp_universal_driver
    Every producer subclasses this FP class, providing functions to translate it's own tables
    to the FPs one and vice versa.
    """
    def __init__(
            self,
            ip: str,
            port: int,
            categories: List[Category],
            plus: List[Plu],
            ivas: List[Iva],
            payments: List[Payment],
            headers: List[Header],
            protocol: Literal['tcp', 'udp'] = 'tcp',
    ):
        self.ip = ip
        self.port = port
        self.protocol = protocol
        assert self.protocol in ['tcp', 'udp'], 'Protocol must be either tcp or udp'
        self.categories = categories
        self.plus = plus
        self.ivas = ivas
        self.payments = payments
        self.headers = headers
        self.sock = None
        self.MAX_TRIES = 3
        self.TRY_DELAY = 0.5
        # Run class validations
        self.__validate__()

    @property
    def max_headers_length(self) -> int:
        raise NotImplementedError('max_headers_length attribute not defined')

    @property
    def max_ivas_length(self) -> int:
        raise NotImplementedError('max_ivas_length attribute not defined')

    @property
    def max_plus_length(self) -> int:
        raise NotImplementedError('max_plus_length attribute not defined')

    @property
    def max_payments_length(self) -> int:
        raise NotImplementedError('max_payments_length attribute not defined')

    @property
    def max_categories_length(self) -> int:
        raise NotImplementedError('max_categories_length attribute not defined')

    def __validate_ip__(self):
        split_ip = self.ip.split('.')
        if len(split_ip) != 4:
            raise AttributeError(f'IP {self.ip} not in IPv4 format')
        for octet in split_ip:
            if not octet.isdigit():
                raise AttributeError(f'IP {self.ip} not in IPv4 format')
            if not 0 <= int(octet) <= 255:
                raise AttributeError(f'IP {self.ip} not in IPv4 format')

    def __validate_port__(self):
        if not 0 < self.port < 65535:
            raise AttributeError(f'Port {self.port} not in range (0, 65535)')

    def __validate_headers__(self):
        if self.max_headers_length != 0:
            if len(self.headers) > self.max_headers_length:
                raise AttributeError(f'Headers max length exceeded ({self.max_headers_length})')

    def __validate_ivas__(self):
        if self.max_ivas_length != 0:
            if len(self.ivas) > self.max_ivas_length:
                raise AttributeError(f'Ivas max length exceeded ({self.max_ivas_length})')

    def __validate_plus__(self):
        if self.max_plus_length != 0:
            if len(self.plus) > self.max_plus_length:
                raise AttributeError(f'Plus max length exceeded ({self.max_plus_length})')
        # Check that all plus reference a valid category
        category_ids = [category.id for category in self.categories]
        for plu in self.plus:
            if plu.category_id not in category_ids:
                raise AttributeError(f'Plu {plu} references a non existent category: {plu.category_id}')

    def __validate_payments__(self):
        if self.max_payments_length != 0:
            if len(self.payments) > self.max_payments_length:
                raise AttributeError(f'Payments max length exceeded ({self.max_payments_length})')

    def __validate_categories__(self):
        if self.max_categories_length != 0:
            if len(self.categories) > self.max_categories_length:
                raise AttributeError(f'Categories max length exceeded ({self.max_categories_length})')
        # Check that all categories reference a valid iva
        iva_ids = [iva.id for iva in self.ivas]
        for category in self.categories:
            if category.iva_id not in iva_ids:
                raise AttributeError(f'Category {category} references a non existent iva: {category.iva_id}')

    def __validate__(self):
        validate(self)
        logger.debug(f'Validations for fp {self} complete')

    def pull_ivas(self):
        raise NotImplementedError('pull_ivas() not implemented')

    def pull_plus(self):
        raise NotImplementedError('pull_plus() not implemented')

    def pull_categories(self):
        raise NotImplementedError('pull_categories() not implemented')

    def pull_payments(self):
        raise NotImplementedError('pull_payments() not implemented')

    def pull_headers(self):
        raise NotImplementedError('pull_headers() not implemented')

    def pull(self):
        self.pull_headers()
        self.pull_ivas()
        self.pull_payments()
        self.pull_categories()
        self.pull_plus()

    def push_ivas(self):
        raise NotImplementedError('push_ivas() not implemented')

    def push_plus(self):
        raise NotImplementedError('push_plus() not implemented')

    def push_categories(self):
        raise NotImplementedError('push_categories() not implemented')

    def push_payments(self):
        raise NotImplementedError('push_payments() not implemented')

    def push_headers(self):
        raise NotImplementedError('push_headers() not implemented')

    def push(self):
        self.push_headers()
        self.push_ivas()
        self.push_payments()
        self.push_categories()
        self.push_plus()

    def to_fp(self) -> 'FP':
        raise NotImplementedError('to_fp() not implemented')

    def from_fp(self, fp: 'FP'):
        raise NotImplementedError('from_fp() not implemented')

    def socket_connect(self):
        if isinstance(self.sock, socket.socket):
            # Check if socket is open
            try:
                self.sock.sendall(b'')
            except BaseException:
                self.socket_disconnect()
        if not isinstance(self.sock, socket.socket):
            if self.protocol == 'tcp':
                # Open a new tcp socket
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            else:
                # Open a new udp socket
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.connect((self.ip, self.port))

    def socket_disconnect(self):
        if isinstance(self.sock, socket.socket):
            self.sock.close()
            self.sock = None

    def send_cmd(self, cmd: bytes) -> Tuple[bool, bytes]:
        try:
            self.socket_connect()
            for i in range(self.MAX_TRIES):
                self.sock.sendall(cmd)
                # Get the response
                response = self.sock.recv(1024)
                has_succeeded, error = self.check_response(response)
                if has_succeeded:
                    return True, response
                else:
                    logger.warning(f"Error while sending command to printer: {error}")
                    time.sleep(self.TRY_DELAY)  # Wait half a second to allow printer buffer to empy
        except socket.timeout as e:
            logger.error(str(e))
            return False, str(e).encode()

    def check_response(self, response: bytes) -> Tuple[bool, str]:
        raise NotImplementedError('check_response() not implemented')

    def __eq__(self, other):
        return is_equal(self, other)


class FP(AbstractFP):
    """
    This class is used to perform tests of the Abstract Parent.
    No real use should be done from this class.
    """
    def __init__(self, *args, **kwargs):
        if 'ip' not in kwargs:
            kwargs['ip'] = '0.0.0.0'
        if 'port' not in kwargs:
            kwargs['port'] = 9100
        if 'categories' not in kwargs:
            kwargs['categories'] = []
        if 'plus' not in kwargs:
            kwargs['plus'] = []
        if 'ivas' not in kwargs:
            kwargs['ivas'] = []
        if 'payments' not in kwargs:
            kwargs['payments'] = []
        if 'headers' not in kwargs:
            kwargs['headers'] = []

        super().__init__(*args, **kwargs)

    @property
    def max_headers_length(self) -> int:
        return 0

    @property
    def max_ivas_length(self) -> int:
        return 0

    @property
    def max_plus_length(self) -> int:
        return 0

    @property
    def max_payments_length(self) -> int:
        return 0

    @property
    def max_categories_length(self) -> int:
        return 0
