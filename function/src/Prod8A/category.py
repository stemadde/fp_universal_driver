from src.category import AbstractCategory


class Category(AbstractCategory):
    def __init__(self, *args, **kwargs):
        if len(args) == 0:
            if 'category_id' not in kwargs:
                kwargs['category_id'] = 1
            if 'description' not in kwargs:
                kwargs['description'] = 'Alimentari'
            if 'default_price' not in kwargs:
                kwargs['default_price'] = 0
            if 'iva_id' not in kwargs:
                kwargs['iva_id'] = 1
        super().__init__(*args, **kwargs)

    @property
    def max_description_length(self) -> int:
        return 20

    def to_fp(self) -> 'Category':
        pass

    def from_fp(self, category: 'Category'):
        pass

    def get_flags(self):
        def b(value):
            return 1 if value else 0

        def s(string):
            return 0 if string == "beni" else 1

        return f'{b(self.is_active)}{b(self.free_price)}00000{s(self.category_type)}0'
