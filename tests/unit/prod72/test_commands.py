import os
from src.Prod72.fp import FP


def get_fp_instance(ip: str, port: int, serial: str):
    fp = FP(
        ip=ip,
        port=port,
        categories=[],
        plus=[],
        ivas=[],
        payments=[],
        headers=[],
        poses=[],
        protocol='tcp',
        serial=serial,
    )
    return fp


def test_info():
    fp = get_fp_instance(
        os.getenv('FP_IP', '192.168.1.10'), int(os.getenv('FP_PORT', '23')), os.getenv('FP_SERIAL', '72MU1106572')
    )
    print('\n\n')


def test_closing():
    fp = get_fp_instance(
        os.getenv('FP_IP', '192.168.1.10'), int(os.getenv('FP_PORT', '23')), os.getenv('FP_SERIAL', '72MU1106572')
    )
    fp.send_closing()
    print('\n\n')


def test_receipt():
    fp = get_fp_instance(
        os.getenv('FP_IP', '192.168.1.10'), int(os.getenv('FP_PORT', '23')), os.getenv('FP_SERIAL', '72MU1106572')
    )
    fp.send_receipt(
        product_list=[
            {
                'quantity': 1000,
                'rep_n': 1,
                'description': 'test',
                'price': 100,
                'iva_id': 1,
            },
            {
                'quantity': 2000,
                'rep_n': 2,
                'description': 'test 2',
                'price': 200,
                'iva_id': 2,
            }
        ],
        payment_list=[
            {
                'payment_id': 1,  # Bonifico
                'amount_paid': 500,
            }
        ]
    )
    print('\n\n')


def test_vp():
    fp = get_fp_instance(
        os.getenv('FP_IP', '192.168.1.10'), int(os.getenv('FP_PORT', '23')), os.getenv('FP_SERIAL', '72MU1106572')
    )
    fp.send_vp(os.getenv('TECH_CF', ''), os.getenv('TECH_VAT', ''), os.getenv('LOTTERY_CODE', ''))
