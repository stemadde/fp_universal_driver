import os
from src.Prod96.fp import FP


def get_fp_instance(ip: str, port: int):
    fp = FP(
        ip=ip,
        port=port,
        categories=[],
        plus=[],
        ivas=[],
        payments=[],
        headers=[],
        poses=[],
        protocol='tcp'
    )
    return fp


def test_closing():
    fp = get_fp_instance(os.getenv('FP_IP', '192.168.1.69'), int(os.getenv('FP_PORT', '9100')))
    fp.send_closing()


def test_receipt():
    fp = get_fp_instance(os.getenv('FP_IP', '192.168.1.69'), int(os.getenv('FP_PORT', '9100')))
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
                'payment_id': 3,  # Bonifico
                'amount_paid': 500,
            }
        ]
    )


def test_vp():
    pass


def test_info():
    fp = get_fp_instance(os.getenv('FP_IP', '192.168.1.69'), int(os.getenv('FP_PORT', '9100')))
    fp.request_fp_data()
