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
    fp.request_fp_data()
