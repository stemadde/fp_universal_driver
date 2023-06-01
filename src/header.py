from abc import ABCMeta
import logging
from .base_fp_object import AbstractFPObject
logger = logging.getLogger(__name__)


class AbstractHeader(AbstractFPObject, metaclass=ABCMeta):
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
        super().__init__()

    @property
    def max_description_length(self) -> int:
        raise NotImplementedError('max_description_length attribute not defined')

    def __validate_max_description_length__(self):
        if len(self.description) > self.max_description_length:
            raise AttributeError(f'Description max length exceeded ({self.max_description_length})')


class Header(AbstractHeader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def max_description_length(self) -> int:
        return 9999
