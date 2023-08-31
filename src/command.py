import datetime
from abc import ABCMeta
from typing import List, Union


class AbstractCommand(metaclass=ABCMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_cmd_bytes(self) -> bytes:
        raise NotImplementedError('get_cmd_bytes() not implemented')

    def get_cmd_byte_list(self) -> List[bytes]:
        raise NotImplementedError('get_cmd_byte_list() not implemented')

    def get_cmd(self) -> Union[bytes, List[bytes]]:
        if self.cmd_return_type == 'bytes':
            return self.get_cmd_bytes()
        elif self.cmd_return_type == 'list':
            return self.get_cmd_byte_list()

    @property
    def cmd_return_type(self) -> str:
        raise NotImplementedError('cmd_return_type() not implemented')


class AbstractInfo(AbstractCommand, metaclass=ABCMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def cmd_return_type(self):
        return 'list'


class AbstractIsReady(AbstractCommand, metaclass=ABCMeta):
    @property
    def cmd_return_type(self):
        return 'bytes'


class AbstractClosing(AbstractCommand, metaclass=ABCMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def cmd_return_type(self):
        return 'bytes'


class AbstractReceipt(AbstractCommand, metaclass=ABCMeta):
    def __init__(self, product_list: List[dict], payment_list: List[dict], *args, **kwargs):
        """
        :param product_list: List of dictionaries with the following structure:
        {
            'description': Optional[str] Product description, if not specified inherited from rep_n
            'price': int,  # Defined as n digits for the integer part and 2 digits for the decimal part
            'quantity': int=1,  # Defined as n digits for the integer part and 3 digits for the decimal part
            'rep_n': int,
            'iva_id': Optional[int],  # ID of the iva in the fp db, if not specified inherited from rep_n
        }
        :param payment_list: List of dictionaries with the following structure:
        {
            'payment_id': int,  # ID of the payment in the fp db
            'amount_paid': int,  # Defined as n digits for the integer part and 2 digits for the decimal part
        }
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.product_list = product_list
        self.payment_list = payment_list
        self.perform_checks()

    def perform_checks(self) -> None:
        """
        Checks if the total amount of payments matches the total amount of products
        """
        total = 0
        for product in self.product_list:
            total += product['price'] * product.get('quantity', 1000)
        total = round(total / 100000)

        payment_total = 0
        for payment in self.payment_list:
            payment_total += payment['amount_paid']
        payment_total = round(payment_total / 100)

        if total - payment_total:
            raise ValueError(
                f'Total amount of payments does not match total amount of products --- Products: {total} --- '
                f'Payments: {payment_total}'
            )

    @property
    def cmd_return_type(self):
        return 'list'


class AbstractVp(AbstractCommand, metaclass=ABCMeta):
    def __init__(
            self,
            fp_serial: str,
            fp_datetime: datetime.datetime,
            current_closing: int,
            perform_first_closing=True,
            send_receipt_1=True,
            send_receipt_2=True,
            delete_receipt_1=True,
            delete_receipt_2=True,
            perform_second_closing=True,
            send_vp_event=True,
            lottery_code='',
            receipt_value_1=112,
            receipt_value_2=134,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        # Steps:
        # 1. Send Closure
        # 2. Send Receipt 1
        # 3. Send Receipt 2 with lottery code
        # 4. Delete Receipt 1
        # 5. Delete Receipt 2
        # 6. Send Closure
        # 7. Send VP event
        self.fp_serial = fp_serial
        self.fp_datetime = fp_datetime
        self.perform_first_closing = perform_first_closing
        self.send_receipt_1 = send_receipt_1
        self.send_receipt_2 = send_receipt_2
        self.delete_receipt_1 = delete_receipt_1
        self.delete_receipt_2 = delete_receipt_2
        self.perform_second_closing = perform_second_closing
        self.send_vp_event = send_vp_event
        self.lottery_code = lottery_code
        self.receipt_value_1 = receipt_value_1
        self.receipt_value_2 = receipt_value_2
        self.current_closing = current_closing
        self.rt_delete_codes = ['8', '1']

        if self.delete_receipt_1:
            assert self.send_receipt_1, 'Cannot delete receipt 1 if it is not sent'
        if self.delete_receipt_2:
            assert self.send_receipt_2, 'Cannot delete receipt 2 if it is not sent'

    def send_closing(self):
        raise NotImplementedError('send_closing() not implemented')

    def send_receipt(self, price: int, lottery_code: str, payment_id: int, description: str = ''):
        raise NotImplementedError('send_receipt() not implemented')

    def delete_receipt(self, receipt_closing_no: int, receipt_progressive_no: int, lottery_code: str):
        raise NotImplementedError('delete_receipt() not implemented')

    def send_vp(self):
        raise NotImplementedError('send_vp() not implemented')

    @property
    def cmd_return_type(self) -> str:
        return 'list'
