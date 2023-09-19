from src.Prod8A.iva import Iva


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
        iva.aliquota_value = iva.max_aliquota_value + 1.0
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
        iva.aliquota_value = iva.min_aliquota_value - 1.0
    except AttributeError:
        pass
    else:
        raise AssertionError('AssertionError not raised for aliquota value < 0')


def test_iva_natura():
    iva = Iva(
        iva_id=6,
        iva_type='natura',
        aliquota_value=None,
        natura_code=0
    )

    assert isinstance(iva, Iva)

    # Set a wrong natura code
    try:
        iva.natura_code = 7
    except AttributeError:
        pass
    else:
        raise AssertionError('AssertionError not raised for natura code N7')

    # Set a wrong natura code, not an integer
    try:
        iva.natura_code = "N1"
    except AttributeError:
        pass
    else:
        raise AssertionError('AssertionError not raised for natura code not integer')


def test_iva_types():
    iva = Iva(
        iva_id=12,
        iva_type='ventilazione',
        aliquota_value=None,
        natura_code=6
    )
    assert isinstance(iva, Iva)

    # Set a wrong iva type
    try:
        iva.iva_type = 'a'
    except AttributeError:
        pass
    else:
        raise AssertionError('AssertionError not raised for iva type a')


def test_wrong_type_and_setting_pairings():
    try:
        Iva(
            iva_id=1,
            iva_type='aliquota',
            aliquota_value=None,
            natura_code=1
        )
    except AttributeError:
        pass
    else:
        raise AssertionError('AssertionError not raised for wrong id and type pairings')

    try:
        Iva(
            iva_id=1,
            iva_type='natura',
            aliquota_value=22.00,
            natura_code=None
        )
    except AttributeError:
        pass
    else:
        raise AssertionError('AssertionError not raised for wrong id and type pairings')

    try:
        Iva(
            iva_id=1,
            iva_type='ventilazione',
            aliquota_value=None,
            natura_code=2
        )
    except AttributeError:
        pass
    else:
        raise AssertionError('AssertionError not raised for wrong id and type pairings')
