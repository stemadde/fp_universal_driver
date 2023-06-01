from typing import List
from typing import TYPE_CHECKING
from src.payment import AbstractPayment

if TYPE_CHECKING:
    from src.Prod8A.fp import FP


class Payment(AbstractPayment):
    def __init__(self, *args, **kwargs):
        if len(args) == 0:
            if 'payment_id' not in kwargs:
                kwargs['payment_id'] = 1
            if 'description' not in kwargs:
                kwargs['description'] = 'Contanti'
            if 'payment_type' not in kwargs:
                kwargs['payment_type'] = 'riscosso'
            if 'payment_subtype' not in kwargs:
                kwargs['payment_subtype'] = 'contanti'

        super().__init__(*args, **kwargs)

    @property
    def max_description_length(self) -> int:
        return 25

    def to_fp(self) -> 'Payment':
        pass

    def from_fp(self, payment: 'Payment'):
        pass

    @staticmethod
    def push(fp: 'FP', objects: List['Payment']):
        pass

    @staticmethod
    def pull(fp: 'FP') -> List['Payment']:
        code = b'{/'
        return_list = []
        for i in range(0, fp.max_payments_length - 1):
            is_successful, response = fp.send_cmd(code + bytes([i + 1]))
            if is_successful:
                # Convert response bytes to ivas
                response = response.decode().split('/')[2:-1]  # Exclude printer status and checksum
                return_list.append(Payment(
                    payment_id=i + 1,
                    description=response[0],
                    payment_type=response[4],
                ))
        return return_list
