from abc import ABCMeta
import logging
from .validator import validate

logger = logging.getLogger(__name__)


class AbstractHeader(metaclass=ABCMeta):
    def __init__(
            self,
            header_id: int,
            description: str,
            is_centered=True,
            is_double_height=False,
            is_double_width=False,
            is_bold=False,
            is_italic=False,
    ):
        self.id = header_id
        self.description = description
        self.is_centered = is_centered
        self.is_double_height = is_double_height
        self.is_double_width = is_double_width
        self.is_bold = is_bold
        self.is_italic = is_italic
        self.__validate__()

    def to_fp(self):
        raise NotImplementedError('to_fp() not implemented')

    def from_fp(self):
        raise NotImplementedError('from_fp() not implemented')

    @property
    def max_description_length(self) -> int:
        raise NotImplementedError('max_description_length attribute not defined')

    def __validate_max_description_length(self):
        assert len(self.description) <= self.max_description_length, \
            f'Description max length exceeded ({self.max_description_length})'

    def __validate__(self):
        """
        Performs validations such as checking that the description provided does not exceed the description max length
        """
        validate(self)
        logger.debug(f'Validations for header {self} complete')


class Header(AbstractHeader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def max_description_length(self) -> int:
        return 9999
