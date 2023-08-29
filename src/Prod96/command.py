import time
from typing import List
import socket
from src.command import AbstractClosing, AbstractReceipt, AbstractCommand


def get_cks(string: bytes) -> bytes:
    total = sum(string)
    out = bytes(str(total)[-2:], "ASCII")
    return out


class Command(AbstractCommand):
    STX = b"\x02"
    ETX = b"\x03"
    ACK = b"\x06"
    IDENT = b"0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frame_cnt = self._FrameCounter()

    def receive_response(self, sock):
        response = sock.recv(256)
        # Keep receiving data until we get an ETX
        while not response.endswith(self.ETX):
            sock.settimeout(180.0)
            response += sock.recv(256)
        return response

    def send(self, bytes_list: List[bytes]) -> bytes:
        # Create a tcp socket and connect it to the specified ip and port
        # Send the command
        # Return the response

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP
        sock.connect((self.ip, self.port), )
        sock.sendall(b'1001')  # Request datetime
        sock.settimeout(180.0)
        # Read the response to the previous command, it contains 14 bytes
        # response = self.receive_response(sock)

        for cmd in bytes_list:
            sock.sendall(cmd)
            sock.settimeout(180.0)
            time.sleep(0.180)
        # response = sock.recv(1024)
        sock.close()
        self.frame_cnt.reset_cnt()
        return b'done'

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


class Closing(AbstractClosing):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self):
        raise NotImplementedError('run() not implemented')


class Receipt(AbstractReceipt, Command):
    SELL_ROW_CMD = '3301' + '1'
    DEFAULT_QUANTITY = 0  # Pad until 9 digits
    DEFAULT_REP_N = 1  # Pad until 3 digits

    PAYMENT_ROW_CMD = '3007'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self) -> bytes:
        # Connect to the fp and send the command
        return self.send(self.convert_commands_to_bytes_list())

    def convert_commands_to_bytes_list(self) -> List[bytes]:

        command_list = []
        for product in self.product_list:
            qty = str(product.get('quantity', self.DEFAULT_QUANTITY)).zfill(9)
            rep_n = str(product.get('rep_n', self.DEFAULT_REP_N)).zfill(3)
            iva_id = str(product.get('iva_id', 0)).zfill(2)
            price = str(product['price']).zfill(9)
            description = product.get('description', '')
            description_length = str(len(description)).zfill(2)
            command = f'{self.SELL_ROW_CMD}{qty}{rep_n}{description_length}{description}{price}{iva_id}'
            command_list.append(self.wrap_cmd(bytes(command, 'ascii')))
        for payment in self.payment_list:
            payment_id = str(payment['payment_id']).zfill(2)
            amount_paid = str(payment['amount_paid']).zfill(9)
            command = f'{self.PAYMENT_ROW_CMD}{payment_id}0000{amount_paid}'
            command_list.append(self.wrap_cmd(bytes(command, 'ascii')))

        command_list.append(self.wrap_cmd(bytes('301120', 'ascii')))  # Close receipt
        command_list.append(self.wrap_cmd(bytes('3013', 'ascii')))  # Cut
        return command_list

    def wrap_cmd(self, cmd):
        cmd_out: bytes = self.frame_cnt.get_cnt() + self.IDENT + cmd
        cmd_out = self.STX + cmd_out + get_cks(cmd_out) + self.ETX
        self.frame_cnt.tick_cnt()
        return cmd_out
