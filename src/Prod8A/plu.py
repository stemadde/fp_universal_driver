from src.plu import AbstractPlu


class Plu(AbstractPlu):
    def __init__(self, *args, **kwargs):
        if len(args) == 0:
            if 'plu_id' not in kwargs:
                kwargs['plu_id'] = 1
            if 'description' not in kwargs:
                kwargs['description'] = 'SP'
            if 'default_price' not in kwargs:
                kwargs['default_price'] = 0
            if 'category_id' not in kwargs:
                kwargs['category_id'] = 1
        super().__init__(*args, **kwargs)

    @property
    def max_description_length(self) -> int:
        return 20  # TODO: Not sure, not found on docs

    def to_fp(self) -> 'Plu':
        pass

    def from_fp(self, plu: 'Plu'):
        pass
