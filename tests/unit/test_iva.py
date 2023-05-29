from src.iva import Iva


def test_iva_aliquota():
    iva = Iva(
        iva_id=1,
        iva_type='aliquota',
        aliquota_value=22.0,
        natura_code=None
    )
    assert isinstance(iva, Iva)

    # Set a wrong aliquota value > 100
    try:
        iva.aliquota_value = 101.0
    except AttributeError:
        pass
    else:
        raise AssertionError('AssertionError not raised for aliquota value > 100')

    # Set a wrong aliquota value, not a number
    try:
        iva.aliquota_value = 'a'
    except AttributeError:
        pass
    else:
        raise AssertionError('AssertionError not raised for aliquota value not float')

    # Set a wrong aliquota value < 0
    try:
        iva.aliquota_value = -1.0
    except AssertionError:
        pass
    else:
        raise AssertionError('AssertionError not raised for aliquota value < 0')
