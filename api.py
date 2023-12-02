from fastapi import FastAPI
from models import *
from main import _vp, _info, _receipt, _closing

app = FastAPI()


@app.post("/vp")
def vp(vp: Vp):
    try:
        _vp(vp)
        return {"message": "running"}
    except NotImplementedError as e:
        return {"message": str(e)}


@app.post("/info")
def info(fp: Fp):
    try:
        return _info(fp)
    except NotImplementedError as e:
        return {"message": str(e)}


@app.post("/receipt")
def receipt(receipt: Receipt, fp: Fp):
    try:
        _receipt(receipt, fp)
        return {"message": "ok"}
    except NotImplementedError as e:
        return {"message": str(e)}


@app.post("/closing")
def closing(fp: Fp):
    try:
        _closing(fp)
        return {"message": "running"}
    except NotImplementedError as e:
        return {"message": str(e)}
