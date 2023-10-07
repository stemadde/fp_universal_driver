import datetime
from decimal import Decimal
from typing import List, Tuple

from src.Prod8A.header import Header
from src.Prod8A.iva import Iva
from src.command import AbstractClosing, AbstractReceipt, AbstractVp, AbstractInfo, AbstractIsReady, AbstractCommand


class Info(AbstractInfo):
    def get_cmd_byte_list(self):
        bytes_list = [b'a', b'0/2/', b'9/', b't/']  # Serial, closing, receipt no, datetime
        return bytes_list

    @staticmethod
    def parse_response(response_list: List[str]) -> Tuple[str, int, int, datetime.datetime]:
        serial = response_list[0]
        serial = serial.split("/")[0]
        closing = response_list[1]
        closing = int(closing.split("/")[0]) + 1
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
        return [b'X']  # receipt state, if ok return 0

    @staticmethod
    def parse_response(response: str) -> bool:
        state = int(response.split("/")[0])
        if state == 0:
            return True
        return False

    @staticmethod
    def is_ready(response: str) -> bool:
        return IsReady.parse_response(response)


class Receipt(AbstractReceipt):
    SELL_ROW_CMD = '3/S'
    DEFAULT_QUANTITY = 0
    DEFAULT_REP_N = 1

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


class Vp(AbstractVp):

    def get_cmd_byte_list(self) -> List[bytes]:
        bytes_list = []
        if self.perform_first_closing:
            bytes_list.append(Closing().get_cmd())

        if self.send_receipt_1:  # Counts as 4 commands
            bytes_list.append(Receipt(
                product_list=[{
                    'rep_n': 1,
                    'description': 'VP 1',
                    'price': self.receipt_value_1,
                    'iva_id': 1,
                }],
                payment_list=[{
                    'payment_id': 1,  # Contanti
                    'amount_paid': self.receipt_value_1,
                }],
            ).get_cmd())

        # Enable lottery
        bytes_list.append(f'I/{self.lottery_code}/0'.encode('ascii'))
        if self.send_receipt_2:  # Counts as 4 commands
            bytes_list.append(Receipt(
                product_list=[{
                    'rep_n': 1,
                    'description': 'VP 2',
                    'price': self.receipt_value_2,
                    'iva_id': 1,
                }],
                payment_list=[{
                    'payment_id': 3,  # Bonifico
                    'amount_paid': self.receipt_value_2,
                }],
            ).get_cmd())

        if self.send_receipt_1:  # Void first receipt
            bytes_list.append(f'+/1/{self.fp_datetime.strftime("%d%m%y")}/{self.current_closing}/1////'.encode('ascii'))
        if self.send_receipt_2:  # Void second receipt
            bytes_list.append(f'+/1/{self.fp_datetime.strftime("%d%m%y")}/{self.current_closing}/2////'.encode('ascii'))
        bytes_list.append(Closing().get_cmd())

        return bytes_list


class HeadersCmd(AbstractCommand):

    def get_cmd_bytes(self) -> bytes:
        return b'O/'

    def send_cmd_bytes(self, header_list: List[Header]) -> bytes:
        return_string = "L"
        for header in header_list:
            return_string += f'/{header.get_formatting_flag()}/{header.description}/{header.get_alignment_flag()}'
        return return_string.encode("ascii")

    @staticmethod
    def parse_response(response: str) -> List[Header]:
        return_list = []
        split = response.split("/")

        for i in range(int(len(split)/2)):
            j = i*2
            descrizione = split[j]
            stripped_descrizione = descrizione.lstrip()
            formattazione = split[j+1]

            header = Header(
                header_id=i+1,
                description=descrizione.strip(),
                is_centered=len(descrizione) != len(stripped_descrizione),
                is_double_height=formattazione in ["1", "3"],
                is_double_width=formattazione in ["2", "3"],
                is_bold=formattazione == '4',
                is_italic=False,
                is_underlined=False
            )
            return_list.append(header)
            if i > 6:
                break
        return return_list

class IvasCmd(AbstractCommand):

    def get_cmd_bytes(self) -> bytes:
        return b'e/'

    @staticmethod
    def parse_response(response: str) -> List[Iva]:
        return_list = []
        split = response.split("/")

        for i in range(int(len(split)/3)):
            valore_iva = Decimal(split[i])
            natura = split[i+12]
            codice_ateco = int(split[i+24])
            codice_natura = 0
            if valore_iva:
                iva_type = "aliquota"
            else:
                codice_natura = int(natura)
                if codice_natura == 6:
                    iva_type = "ventilazione"
                else:
                    iva_type = "natura"

            iva = Iva(
                iva_id=i+1,
                iva_type=iva_type,
                aliquota_value=valore_iva,
                natura_code=codice_natura,
                ateco_code=codice_ateco
            )
            return_list.append(iva)
        return return_list

    @staticmethod
    def send_cmd_bytes(iva_list: List[Iva]) -> bytes:
        return_string = "b"
        for i in range(3):
            for iva in iva_list:
                if i == 0:
                    return_string += f'/{iva.aliquota_value}'
                elif i == 1:
                    return_string += f'/{iva.natura_code}'
                else:
                    return_string += f'/{iva.ateco_code}'
        return return_string.encode("ascii")
