from typing import Optional


class Category:
    def __init__(
            self,
            category_id: int,
            description: str,
            default_price: Optional[float],
            max_price: Optional[float],
            min_price: Optional[float],
            iva_id: int,
    ):
        self.category_id = category_id
        self.description = description
        self.default_price = default_price
        self.max_price = max_price
        self.min_price = min_price
        self.iva_id = iva_id

    def to_fp(self):
        raise NotImplementedError('to_fp() not implemented')

    def from_fp(self):
        raise NotImplementedError('from_fp() not implemented')

    @property
    def max_description_length(self) -> int:
        """
        When inheriting overwrite this with the max number of chars supported by the protocol
        """
        raise NotImplementedError('max_description_length attribute not defined')

    def __validate__(self):
        """
        Performs validations such as checking that the description provided does not exceed the description max length
        """
        assert len(self.description) <= self.max_description_length, \
            f'Description max length exceeded ({self.max_description_length})'
