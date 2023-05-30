from src.payment import AbstractPayment


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
