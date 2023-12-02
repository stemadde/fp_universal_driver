from typing import Type
from src.iva import Iva
from src.payment import Payment
from src.header import Header
from src.category import Category
from src.plu import Plu
from src.fp import FP, AbstractFP
from src.pos import Pos


def create_instances() -> tuple:
    # Create Iva, Payment, Header, Category, Plus
    iva = Iva(
        iva_id=1,
        iva_type='natura',
        aliquota_value=None,
        natura_code='N1'
    )

    payment = Payment(
        payment_id=1,
        description='Bonifico',
        payment_type='riscosso',
        payment_subtype='elettronico',
        drawer_open=False,
        require_value=True,
        pos_id=1,
    )

    header = Header(
        header_id=1,
        description='SP di Maddè Stefano',
    )

    category = Category(
        category_id=1,
        description='Alimentari',
        default_price=1.0,
        max_price=99.0,
        min_price=0.0,
        iva_id=1,
    )

    plu = Plu(
        plu_id=1,
        description='Pasta',
        category_id=1,
        default_price=1.0,
    )

    pos = Pos(
        pos_id=1,
        description='Pos 1',
        ip='192.168.1.2',
        port=9100,
        protocol='ingenico',
    )

    return iva, payment, header, category, plu, pos


def correct_fp_config(fp_class: Type[AbstractFP], ip='0.0.0.0', port=9100):
    # Create Iva, Payment, Header, Category, Plus
    iva, payment, header, category, plu, pos = create_instances()

    # Now instance FP - all the above objects are passed as arguments and are correct
    fp = fp_class(
        ip=ip,
        port=port,
        ivas=[iva],
        payments=[payment],
        headers=[header],
        categories=[category],
        plus=[plu],
        poses=[pos],
    )
    return fp


def wrong_id_references(fp_class: Type[AbstractFP], ip='0.0.0.0', port=9100):
    # Create Iva, Payment, Header, Category, Plus
    iva, payment, header, category, plu, pos = create_instances()

    # Set a category to a wrong iva_id
    category.iva_id = 2
    # Now build a new FP with a wrong category
    try:
        fp_class(
            ip=ip,
            port=port,
            ivas=[iva],
            payments=[payment],
            headers=[header],
            categories=[category],
            plus=[plu],
            poses=[pos],
        )
    except AttributeError:
        # If error is raised correctly restore the correct iva_id
        category.iva_id = 1
    else:
        raise AssertionError('AssertionError not raised for wrong iva_id inside a category config')

    # Set a plu to a wrong category_id
    plu.category_id = 2
    # Now build a new FP with a wrong plu
    try:
        fp_class(
            ip=ip,
            port=port,
            ivas=[iva],
            payments=[payment],
            headers=[header],
            categories=[category],
            plus=[plu],
            poses=[pos],
        )
    except AttributeError:
        # If error is raised correctly restore the correct category_id
        plu.category_id = 1
    else:
        raise AssertionError('AssertionError not raised for wrong category_id inside a plu config')

    # Set a payment to a wrong pos_id
    payment.pos_id = 2
    # Now build a new FP with a wrong payment
    try:
        fp_class(
            ip=ip,
            port=port,
            ivas=[iva],
            payments=[payment],
            headers=[header],
            categories=[category],
            plus=[plu],
            poses=[pos],
        )
    except AttributeError:
        # If error is raised correctly restore the correct pos_id
        payment.pos_id = 1
    else:
        raise AssertionError('AssertionError not raised for wrong pos_id inside a payment config')

    # Set a payment to a type-subtype combination and link to pos
    try:
        payment.payment_subtype = 'contanti'
    except AttributeError:
        # If error is raised correctly restore the correct payment_type
        pass
    else:
        raise AssertionError('AssertionError not raised for wrong payment_type when using with pos')


def test_std_fp():
    fp = correct_fp_config(FP)
    assert isinstance(fp, FP)
    wrong_id_references(FP)
