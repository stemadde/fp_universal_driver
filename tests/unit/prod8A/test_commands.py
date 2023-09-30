import os

from src.Prod8A.fp import FP


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
        os.getenv('FP_IP', '192.168.1.76'), int(os.getenv('FP_PORT', '9101')), os.getenv('FP_SERIAL', '8AMTN024519')
    )
    fp.send_closing()


def test_info():
    fp = get_fp_instance(
        os.getenv('FP_IP', '192.168.1.76'), int(os.getenv('FP_PORT', '9101')), os.getenv('FP_SERIAL', '8AMTN024519')
    )
    print('\n\n')
    fp.request_fp_data()


def test_vp():
    fp = get_fp_instance(
        os.getenv('FP_IP', '192.168.1.76'), int(os.getenv('FP_PORT', '9101')), os.getenv('FP_SERIAL', '8AMTN024519')
    )
    fp.send_vp(os.getenv('TECH_CF', ''), os.getenv('TECH_VAT', ''), os.getenv('LOTTERY_CODE', ''))
