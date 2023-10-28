import datetime
from typing import List, Tuple

from src.Prod96.category import Category
from src.Prod96.header import Header
from src.command import AbstractClosing, AbstractReceipt, AbstractVp, AbstractInfo, AbstractIsReady, AbstractCommand


class Info(AbstractInfo):
    def get_cmd_byte_list(self) -> List[bytes]:
        bytes_list = [b'1008', b'1104', b'1017', b'1001']  # Serial, closing, receipt no, datetime
        return bytes_list

    @staticmethod
    def parse_response(response_list: List[str]) -> Tuple[str, int, int, datetime.datetime]:
        serial = response_list[0][6:6+8]
        current_closing = response_list[1]
        current_closing = int(current_closing[4:8])
        current_receipt = response_list[2]
        current_receipt = int(current_receipt[14:18])
        fp_datetime = response_list[3][4:4+len('ddmmyyhhmm')]
        fp_datetime = datetime.datetime.strptime(fp_datetime, "%d%m%y%H%M")
        return serial, current_closing, current_receipt, fp_datetime


class IsReady(AbstractIsReady):
    def get_cmd_byte_list(self) -> List[bytes]:
        return [b'1513', b'1509', b'1021']

    @staticmethod
    def parse_response(response: str) -> bool:
        if response.startswith('1513'):
            return True
        if response.startswith('1509'):
            return response[4:].startswith('0000000')
        if response.startswith('1021'):
            return response[4:].startswith('00')
        return False

    @staticmethod
    def is_ready(response: str) -> bool:
        return IsReady.parse_response(response)


class Closing(AbstractClosing):
    def get_cmd_bytes(self) -> bytes:
        return b'220201'


class Receipt(AbstractReceipt):
    SELL_ROW_CMD = '3301' + '1'
    DEFAULT_QUANTITY = 0  # Pad until 9 digits
    DEFAULT_REP_N = 1  # Pad until 3 digits

    PAYMENT_ROW_CMD = '3007'

    def get_cmd_byte_list(self) -> List[bytes]:
        command_list = []
        for product in self.product_list:
            qty = str(product.get('quantity', self.DEFAULT_QUANTITY)).zfill(9)
            rep_n = str(product.get('rep_n', self.DEFAULT_REP_N)).zfill(3)
            iva_id = str(product.get('iva_id', 0)).zfill(2)
            price = str(product['price']).zfill(9)
            description = product.get('description', '')
            description_length = str(len(description)).zfill(2)
            command = f'{self.SELL_ROW_CMD}{qty}{rep_n}{description_length}{description}{price}{iva_id}'
            command_list.append(bytes(command, 'ascii'))
        for payment in self.payment_list:
            payment_id = str(payment['payment_id']).zfill(2)
            amount_paid = str(payment['amount_paid']).zfill(9)
            command = f'{self.PAYMENT_ROW_CMD}{payment_id}0000{amount_paid}'
            command_list.append(bytes(command, 'ascii'))

        command_list.append(bytes('301120', 'ascii'))  # Close receipt
        command_list.append(bytes('3013', 'ascii'))  # Cut
        return command_list


class Vp(AbstractVp):
    def get_cmd_byte_list(self) -> List[bytes]:
        bytes_list = []
        if self.perform_first_closing:
            bytes_list.append(Closing().get_cmd())
            self.current_closing += 1

        # Start intervention
        bytes_list.append(b'64040')

        if self.send_receipt_1:  # Counts as 4 commands
            bytes_list.append(Receipt(
                product_list=[{
                    'rep_n': 1,
                    'description': 'VP 1',
                    'price': self.receipt_value_1,
                    'iva_id': 1,
                }],
                payment_list=[{
                    'payment_id': 3,  # Bonifico
                    'amount_paid': self.receipt_value_1,
                }],
            ).get_cmd())
        # Enable lottery
        bytes_list.append(f'3019{str(len(self.lottery_code)).zfill(2)}{self.lottery_code.upper()}'.encode('ascii'))
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

        # Receipt deletion
        if self.delete_receipt_1:
            for code in self.rt_delete_codes:
                cmd = (f'7101A'
                       f'{str(self.current_closing + 1).zfill(4)}'
                       f'0001'
                       f'{self.fp_datetime.strftime("%d%m%y")}'
                       f'{code}'
                       # f'{len(self.fp_serial)}{self.fp_serial}'
                       )
                bytes_list.append(cmd.encode('ascii'))
        if self.delete_receipt_2:
            for code in self.rt_delete_codes:
                cmd = (f'7101A'
                       f'{str(self.current_closing + 1).zfill(4)}'
                       f'0002'
                       f'{self.fp_datetime.strftime("%d%m%y")}'
                       f'{code}'
                       # f'{len(self.fp_serial)}{self.fp_serial}'
                       # f'{len(self.lottery_code)}{self.lottery_code}'
                       )
                bytes_list.append(cmd.encode('ascii'))

        bytes_list.append(Closing().get_cmd())
        self.current_closing += 1
        bytes_list.append(f'5001{str(self.current_closing-1).zfill(4)}{str(self.current_closing-1).zfill(4)}'.encode('ascii'))
        bytes_list.append(f'8003{str(self.current_closing-1).zfill(4)}{str(self.current_closing-1).zfill(4)}0'.encode('ascii'))

        if self.send_vp_event:
            cmd = '640413'
            cf = self.tech_cf
            cf = f'{len(cf)}{cf}'
            piva = self.tech_vat
            piva = f'{len(piva)}{piva}'
            description = 'VP OK'
            description = f'{str(len(description)).zfill(2)}{description}'
            bytes_list.append(f'{cmd}{cf}{piva}{description}'.encode('ascii'))

        return bytes_list

class CategoryCmd(AbstractCommand):
    def get_cmd_byte(self) -> bytes:
        return b'2103'

    @staticmethod
    def parse_response(response_list: List[str]) ->List[Category]:
        return_list = []
        for i, category in enumerate(response_list):
            description = split[0]
            iva = split[1]
            category_id = i+1
            default_price = Decimal(split[3])
            max_price = Decimal(split[4])
            flags = split[6]
            is_active = bool(int(flags[0]))
            free_price = bool(int(flags[1]))
            category_type = "beni" if flags[7] == "0" else "servizi"

            category = Category(
                category_id=category_id,
                description=description,
                default_price=default_price,
                iva_id=iva,
                max_price=max_price,
                is_active=is_active,
                free_price=free_price,
                category_type=category_type,
            )
            return_list.append(category)
        return return_list

    @staticmethod
    def send_cmd_byte_list(category_list: List[Category]) -> List[bytes]:
        return_list = []
        for category in category_list:
            return_string = "N"
            return_string += f'/{category.id}'
            return_string += f'/{category.description}'
            return_string += f'/{category.iva_id}'
            return_string += f'/1'
            return_string += f'/{category.default_price}'
            return_string += f'/{category.max_price}'
            return_string += f'/0.00'
            return_string += f'/{category.get_flags()}'
            return_string += '//'
            return_list.append(return_string.encode("ascii"))
        return return_list


class HeadersCmd(AbstractCommand):

    def get_cmd_bytes_list(self, max_headers_length: int) -> List[bytes]:
        list_header = []
        for i in range(max_headers_length):
            list_header.append(f"1002{i+1}".encode("ascii"))
        return list_header

    def send_cmd_bytes(self, header_list: List[Header]) -> bytes:
        return_string = "L"
        for header in header_list:
            return_string += f'/{header.get_formatting_flag()}/{header.description}/{header.get_alignment_flag()}'
        return return_string.encode("ascii")

    @staticmethod
    def parse_response(response: List[str]) -> List[Header]:
        return_list = []

        for i, riga in enumerate(response):
            riga = riga[5:]
            flag = riga[0]
            lunghezza = riga[1:3]
            descrizione = riga[3:]

            header = Header(
                header_id=i+1,
                description=descrizione.strip(),
                is_centered=True,
                is_double_height=flag == '4',
                is_double_width=flag == '5',
                is_bold=flag == '2',
                is_italic=flag == '6',
                is_underlined=False
            )
            return_list.append(header)
            if i > 6:
                break
        return return_list
