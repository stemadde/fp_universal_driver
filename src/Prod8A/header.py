from src.header import AbstractHeader, Header as StdHeader


class Header(AbstractHeader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def max_description_length(self) -> int:
        return 48

    def __validate_id__(self):
        if not 1 <= self.id <= 8:
            raise AttributeError('Id is not in range 1 - 8')

    def to_fp(self) -> StdHeader:
        return StdHeader(
            header_id=self.id,
            description=self.description,
            is_centered=self.is_centered,
            is_double_height=self.is_double_height,
            is_double_width=self.is_double_width,
            is_bold=self.is_bold,
            is_italic=self.is_italic
        )

    def from_fp(self, header: 'Header'):
        self.id = header.id
        self.description = header.description
        self.is_centered = header.is_centered
        self.is_double_height = header.is_double_height
        self.is_double_width = header.is_double_width
        self.is_bold = header.is_bold
        self.is_italic = header.is_italic
        self.__validate__()

    def convert_to_cmd(self) -> bytes:
        first_byte = 0
        if self.is_bold:
            first_byte = 4
        elif self.is_double_width and self.is_double_height:
            first_byte = 3
        elif self.is_double_width:
            first_byte = 2
        elif self.is_double_height:
            first_byte = 1
        last_byte = 0
        if not self.is_centered:
            last_byte = 1
        return f'{first_byte}/{self.description}/{last_byte}/'.encode()
