import os
import time
from src.Prod96.command import Vp
from src.Prod96.fp import FP


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


def test_closing():
    fp = get_fp_instance(
        os.getenv('FP_IP', '192.168.1.69'), int(os.getenv('FP_PORT', '9100')), os.getenv('FP_SERIAL', 'STMTE770910')
    )
    fp.send_closing()


def test_receipt():
    fp = get_fp_instance(
        os.getenv('FP_IP', '192.168.1.69'), int(os.getenv('FP_PORT', '9100')), os.getenv('FP_SERIAL', 'STMTE770910')
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
                'payment_id': 3,  # Bonifico
                'amount_paid': 500,
            }
        ]
    )


def test_vp():
    fp = get_fp_instance(
        os.getenv('FP_IP', '192.168.1.69'), int(os.getenv('FP_PORT', '9100')), os.getenv('FP_SERIAL', 'STMTE770910')
    )
    fp.send_vp(os.getenv('TECH_CF', ''), os.getenv('TECH_VAT', ''), os.getenv('LOTTERY_CODE', ''))


def test_vp_last_step():
    fp = get_fp_instance(
        os.getenv('FP_IP', '192.168.1.69'), int(os.getenv('FP_PORT', '9100')), os.getenv('FP_SERIAL', 'STMTE770910')
    )
    cmd_list = Vp(
        fp_serial=fp.serial,
        fp_datetime=fp.fp_datetime,
        current_closing=fp.current_closing,
        lottery_code='UF7KDL1T',
        receipt_value_1=112,
        receipt_value_2=134,
        perform_first_closing=False,
    ).get_cmd()
    step_list = [
        # 1, 2, 3, 4,  # First receipt
        # 5, 6, 7, 8,  # Second receipt
        10, 11,  # Delete first receipt
        12, 13,  # Delete second receipt
    ]
    for step in step_list:
        print(cmd_list[step])
        is_successful, response = fp.send_cmd(cmd_list[step])
        time.sleep(1)
        print(fp.unwrap_response(response))


def test_info():
    fp = get_fp_instance(
        os.getenv('FP_IP', '192.168.1.69'), int(os.getenv('FP_PORT', '9100')), os.getenv('FP_SERIAL', 'STMTE770910')
    )
    print('\n\n')
    fp.request_fp_data()
