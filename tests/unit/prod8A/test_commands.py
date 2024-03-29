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


def test_headers():
    fp = get_fp_instance(
        os.getenv('FP_IP', '192.168.1.76'), int(os.getenv('FP_PORT', '9101')), os.getenv('FP_SERIAL', '8AMTN024519')
    )
    fp.get_headers()
    fp.headers[0].description = fp.headers[0].description[::-1]
    fp.send_headers()


def test_ivas():
    fp = get_fp_instance(
        os.getenv('FP_IP', '192.168.1.76'), int(os.getenv('FP_PORT', '9101')), os.getenv('FP_SERIAL', '8AMTN024519')
    )
    fp.get_ivas()
    iva = fp.ivas[0]
    fp.ivas[0] = fp.ivas[1]
    fp.ivas[1] = iva
    fp.send_ivas()

def test_categories():
    fp = get_fp_instance(
        os.getenv('FP_IP', '192.168.1.76'), int(os.getenv('FP_PORT', '9101')), os.getenv('FP_SERIAL', '8AMTN024519')
    )
    fp.get_category()
    category_id = fp.categories[0].id
    fp.categories[0].id = fp.categories[1].id
    fp.categories[1].id = category_id
    fp.send_category()

def test_poses():
    fp = get_fp_instance(
        os.getenv('FP_IP', '192.168.1.76'), int(os.getenv('FP_PORT', '9101')), os.getenv('FP_SERIAL', '8AMTN024519')
    )
    fp.get_pos()
    pos_id = fp.poses[0].id
    fp.poses[0].id = fp.poses[1].id
    fp.poses[1].id = pos_id
    fp.send_pos()
