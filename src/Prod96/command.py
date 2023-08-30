from typing import List
from src.command import AbstractClosing, AbstractReceipt, AbstractVp


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

        if self.send_receipt_1:
            bytes_list.append(Receipt(
                product_list=[{
                    'rep_n': 1,
                    'description': 'VP 1',
                    'price': 123,
                    'iva_id': 1,
                }],
                payment_list=[{
                    'payment_id': 1,  # Contanti
                    'amount_paid': 123,
                }],
            ).get_cmd())
        if self.send_receipt_2:
            bytes_list.append(Receipt(
                product_list=[{
                    'rep_n': 1,
                    'description': 'VP 2',
                    'price': 134,
                    'iva_id': 1,
                }],
                payment_list=[{
                    'payment_id': 3,  # Bonifico
                    'amount_paid': 134,
                }],
            ).get_cmd())
        if self.delete_receipt_1:
            pass
        if self.delete_receipt_2:
            pass
        if self.perform_second_closing:
            bytes_list.append(Closing().get_cmd())
        if self.send_vp_event:
            cmd = '640413'
            cf = 'MDDSFN98D02M102A'
            cf = f'{len(cf)}{cf}'
            piva = '11512940963'
            piva = f'{len(piva)}{piva}'
            description = 'VP OK'
            description = f'{len(description)}{description}'
            bytes_list.append(f'{cmd}{cf}{piva}{description}'.encode('ascii'))

        return bytes_list
