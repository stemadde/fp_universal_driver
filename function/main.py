import os
from typing import Optional
from fastapi import FastAPI
import threading
from models import Vp, Fp, Receipt

app = FastAPI()
BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def get_fp_instance(fp_class: type, fp_params: Fp):
    fp = fp_class(
        ip=fp_params.ip,
        port=fp_params.port,
        categories=[],
        plus=[],
        ivas=[],
        payments=[],
        headers=[],
        poses=[],
        protocol=fp_params.protocol,
        serial=fp_params.serial,
    )
    return fp


def get_fp_class(fp_producer: str) -> Optional[type]:
    fp_class = None
    if fp_producer == '96':
        from src.Prod96.fp import FP
        fp_class = FP
    elif fp_producer == '8A':
        from src.Prod8A.fp import FP
        fp_class = FP
    return fp_class


def _vp(vp: Vp):
    producer = vp.fp.producer
    vp_args = {
        "value1": vp.receipt_1.receipt_value,
        "value2": vp.receipt_2.receipt_value,
        "lottery_code": vp.receipt_1.receipt_lottery_code if vp.receipt_1.receipt_lottery_code else vp.receipt_2.receipt_lottery_code,
        "tech_cf": vp.tech_cf,
        "tech_vat": vp.tech_vat,
    }
    fp = get_fp_instance(get_fp_class(producer), vp.fp)
    if fp is None:
        raise NotImplementedError(f"Producer {producer} not supported")
    t = threading.Thread(target=fp.send_vp, kwargs=vp_args)
    t.start()
    return None


def _info(fp: Fp):
    fp_instance = get_fp_instance(get_fp_class(fp.producer), fp)
    if fp_instance is None:
        raise NotImplementedError(f"Producer {fp.producer} not supported")
    result = fp_instance.serialize()
    return result


def _receipt(receipt: Receipt, fp: Fp):
    fp_instance = get_fp_instance(get_fp_class(fp.producer), fp)
    if fp_instance is None:
        raise NotImplementedError(f"Producer {fp.producer} not supported")
    fp_instance.send_receipt(**receipt.to_internal())
    return None


def _closing(fp: Fp):
    fp_instance = get_fp_instance(get_fp_class(fp.producer), fp)
    if fp_instance is None:
        raise NotImplementedError(f"Producer {fp.producer} not supported")
    t = threading.Thread(target=fp_instance.send_closing)
    t.start()
    return None


if __name__ == '__main__':
    # get args and kwargs
    import argparse
    parser = argparse.ArgumentParser(description='Run the server')
    # Required argument --target, must be one of the functions name in this file
    parser.add_argument(
        '-t', '--target', type=str, required=True,
        choices=['info', 'vp', 'receipt', 'closing']
    )
    parser.add_argument('-p', '--producer', type=str, required=True)
    parser.add_argument('--ip', type=str, required=True)
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--serial', type=str, required=True)
    parser.add_argument('--protocol', type=str, default='tcp')

    """
    parser.add_argument('--tech_cf', type=str, default='')
    parser.add_argument('--tech_vat', type=str, default='')
    parser.add_argument('--receipt_1', type=str, default='')
    parser.add_argument('--receipt_2', type=str, default='')
    parser.add_argument('--receipt_lottery_code', type=str, default='')
    """

    args = parser.parse_args()
    kwargs = vars(args)
    # run the server
    print(kwargs)
    # Run the function described in the target argument
    if kwargs['target'] == 'info':
        res = _info(Fp(**kwargs))
    elif kwargs['target'] == 'vp':
        res = _vp(Vp(**kwargs))
    elif kwargs['target'] == 'receipt':
        res = _receipt(Receipt(**kwargs), Fp(**kwargs))
    elif kwargs['target'] == 'closing':
        res = _closing(Fp(**kwargs))
    else:
        raise NotImplementedError(f"Target {kwargs['target']} not supported")
    print(res)
