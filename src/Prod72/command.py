import datetime
from typing import List, Tuple
from src.command import AbstractClosing, AbstractReceipt, AbstractVp, AbstractInfo, AbstractIsReady


class Info(AbstractInfo):
    def get_cmd_byte_list(self):
        bytes_list = [b'<</?s', b'<</?m', b'<</?7', b'<</?d']  # General, Serial, closing, datetime
        return bytes_list

    @staticmethod
    def parse_response(response_list: List[str]) -> Tuple[str, int, int, datetime.datetime]:
        serial = response_list[1]
        chiusura = int(response_list[2])
        num_scontrino = int(response_list[0][-4:])
        data = datetime.datetime.strptime(response_list[3], "%d/%m/%Y %H:%M:%S")
        return serial, chiusura, num_scontrino, data


class Closing(AbstractClosing):
    def get_cmd_byte_list(self) -> List[bytes]:
        return [b'=C3', b'=C10', b'=C1']


class Receipt(AbstractReceipt):
    SELL_ROW_CMD = '=R'
    DEFAULT_QUANTITY = 1000
    DEFAULT_REP_N = 1

    PAYMENT_ROW_CMD = '=T'

    def get_cmd_byte_list(self) -> List[bytes]:
        command_list = [b'=C1']
        for product in self.product_list:
            qty = str(product.get('quantity', self.DEFAULT_QUANTITY)).zfill(4)
            qty = qty[:-3]+"."+qty[-3:]
            rep_n = str(product.get('rep_n', self.DEFAULT_REP_N))
            price = str(product['price']).zfill(3)
            description = product.get('description', '')
            command = f'{self.SELL_ROW_CMD}{rep_n}/${price}/*{qty}/({description})'
            command_list.append(bytes(command, 'ascii'))
        for payment in self.payment_list:
            payment_id = str(payment['payment_id'])
            amount_paid = str(payment['amount_paid']).zfill(3)
            command = f'{self.PAYMENT_ROW_CMD}{payment_id}/${amount_paid}'
            command_list.append(bytes(command, 'ascii'))
        command_list.append(f"{self.PAYMENT_ROW_CMD}1".encode("ascii"))
        command_list.append(b'=K')

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
        bytes_list.append(f'="/?L/$1/({self.lottery_code})'.encode('ascii'))
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
            bytes_list.append(f'=k/&{self.fp_datetime.strftime("%d%m%y")}/[{self.current_closing}/]1'.encode('ascii'))
        if self.send_receipt_2:  # Void second receipt
            bytes_list.append(f'=k/&{self.fp_datetime.strftime("%d%m%y")}/[{self.current_closing}/]2'.encode('ascii'))
        bytes_list.append(Closing().get_cmd())
        bytes_list.append(b'=C5')
        bytes_list.append(b'=C805/$0/3')
        bytes_list.append(b'=C805/$1/(VP OK)')
        bytes_list.append(f'=C805/$2/({self.tech_cf})'.encode("ascii"))
        bytes_list.append(b'=C805/$3/(IT)')
        bytes_list.append(f'=C805/$4/({self.tech_vat})'.encode("ascii"))
        bytes_list.append(b'=C805/$5')
        bytes_list.append(Closing().get_cmd())

        return bytes_list
