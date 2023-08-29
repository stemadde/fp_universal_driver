from abc import ABCMeta
from typing import List


class AbstractCommand(metaclass=ABCMeta):
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

    def send(self, bytes_list: List[bytes]) -> bytes:
        raise NotImplementedError('send() not implemented')


class AbstractClosing(AbstractCommand, metaclass=ABCMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run()

    def run(self):
        raise NotImplementedError('run() not implemented')


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
        self.run()

    def perform_checks(self) -> None:
        """
        Checks if the total amount of payments matches the total amount of products
        """
        total = 0
        for product in self.product_list:
            total += product['price'] * product['quantity']
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

    def run(self):
        raise NotImplementedError('run() not implemented')
