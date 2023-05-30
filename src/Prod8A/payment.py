from src.payment import AbstractPayment


class Payment(AbstractPayment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
