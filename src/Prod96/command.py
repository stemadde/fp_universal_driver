import datetime
from typing import List, Tuple
from src.command import AbstractClosing, AbstractReceipt, AbstractVp, AbstractInfo, AbstractIsReady


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
                    'payment_id': 1,  # Contanti
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

        if self.perform_second_closing:
            bytes_list.append(Closing().get_cmd())

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
