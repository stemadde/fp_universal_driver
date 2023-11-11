import configparser
import os
from typing import Union, Optional

from fastapi import FastAPI
import threading
from models import Vp, Fp, Receipt

app = FastAPI()
BASE_PATH = os.path.dirname(os.path.abspath(__file__))


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


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


@app.post("/vp")
def vp(vp: Vp):

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
        return {"message": "Producer not supported"}
    t = threading.Thread(target=fp.send_vp, kwargs=vp_args)
    t.start()
    return {"message": "running"}


@app.post("/info")
def info(fp: Fp):
    fp_instance = get_fp_instance(get_fp_class(fp.producer), fp)
    if fp_instance is None:
        return {"message": "Producer not supported"}
    result = fp_instance.serialize()
    return {"message": "ok", "data": result}


@app.post("/receipt")
def receipt(receipt: Receipt, fp: Fp):
    fp_instance = get_fp_instance(get_fp_class(fp.producer), fp)
    if fp_instance is None:
        return {"message": "Producer not supported"}
    fp_instance.send_receipt(**receipt.to_internal())
    return {"message": "ok"}

@app.post("/closing")
def closing(fp: Fp):
    fp_instance = get_fp_instance(get_fp_class(fp.producer), fp)
    if fp_instance is None:
        return {"message": "Producer not supported"}
    t = threading.Thread(target=fp_instance.send_closing)
    t.start()
    return {"message": "ok"}
