import datetime
from typing import List, Tuple
from src.command import AbstractClosing, AbstractReceipt, AbstractVp, AbstractInfo, AbstractIsReady


class Info(AbstractInfo):
    def cmd_return_type(self):
        return 'list'

    def get_cmd_byte_list(self):
        bytes_list = [b'a', b'0/2/', b'9/', b't/']  # Serial, closing, receipt no, datetime
        return bytes_list

    @staticmethod
    def parse_response(response_list: List[str]) -> Tuple[str, int, int, datetime.datetime]:
        serial = response_list[0]
        serial = serial.split("/")[0]
        closing = response_list[1]
        closing = int(closing.split("/")[0])
        receipt = response_list[2]
        receipt = int(receipt.split("/")[5])
        date = response_list[3]
        date = datetime.datetime.strptime(date, "%d%m%y/%H%M%S")
        return serial, closing, receipt, date


class Closing(AbstractClosing):
    def get_cmd_bytes(self) -> bytes:
        return b'x/7//////'


class IsReady(AbstractIsReady):

    def get_cmd_byte_list(self) -> List[bytes]:
        return [b'X', b'1509', b'1021']  #stato scontrino,

    @staticmethod
    def parse_response(response: str) -> bool:
        if response.startswith('X'):
            tipo_stato = response[0]
            tipo_stato = int(tipo_stato.split("/")[0])
            if tipo_stato == 0:
                return True
        return False

    @staticmethod
    def is_ready(response: str) -> bool:
        return IsReady.parse_response(response)

class Receipt(AbstractReceipt):
    SELL_ROW_CMD = '3/S'
    DEFAULT_QUANTITY = 0  # Pad until 9 digits
    DEFAULT_REP_N = 1  # Pad until 3 digits

    PAYMENT_ROW_CMD = '5'

    def get_cmd_byte_list(self) -> List[bytes]:
        command_list = []
        for product in self.product_list:
            qty = str(product.get('quantity', self.DEFAULT_QUANTITY)).zfill(4)
            qty = qty[:-3]+"."+qty[-3:]
            rep_n = str(product.get('rep_n', self.DEFAULT_REP_N))
            price = str(product['price']).zfill(3)
            price = price[:-2]+"."+price[-2:]
            description = product.get('description', '')
            command = f'{self.SELL_ROW_CMD}/{description}//{qty}/{price}/{rep_n}/////'
            command_list.append(bytes(command, 'ascii'))
        for payment in self.payment_list:
            payment_id = str(payment['payment_id'])
            amount_paid = str(payment['amount_paid']).zfill(3)
            amount_paid = amount_paid[:-2]+"."+amount_paid[-2:]
            command = f'{self.PAYMENT_ROW_CMD}/{payment_id}/{amount_paid}///////'
            command_list.append(bytes(command, 'ascii'))

        return command_list
