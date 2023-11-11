from decimal import Decimal
from typing import Union, Literal, List
from pydantic.networks import IPv4Network
from pydantic import BaseModel


class Fp(BaseModel):
    producer: str
    ip: str
    port: int
    protocol: Literal["tcp", "udp"]
    serial: str


class Payment(BaseModel):
    payment_id: int = 3
    amount_paid: int = 0


class Product(BaseModel):
    price: int
    quantity: int = 1000
    rep_n: int = 1
    description: str = "test"
    iva_id: int = 1


class Receipt(BaseModel):
    product_list: List[Product]
    payment_list: List[Payment]
    receipt_lottery_code: str

    def to_internal(self):
        p_list = []
        pay_list = []
        amount = Decimal("0.00")
        for product in self.product_list:
            p_list.append(dict(product))
            price = str(product.price).zfill(3)
            price = price[:-2] + "." + price[-2:]
            quantity = str(product.quantity).zfill(4)
            quantity = quantity[:-3] + "." + quantity[-3:]
            amount += Decimal(price) * Decimal(quantity)
        amount = int(str(amount.quantize(2)).replace(".", ""))
        if len(self.payment_list) == 1 and not self.payment_list[0].amount_paid:
            self.payment_list[0].amount_paid = amount
        for payment in self.payment_list:
            pay_list.append(dict(payment))
        return {
            "product_list": p_list,
            "payment_list": pay_list
        }


class Vp(BaseModel):
    fp: Fp
    receipt_1: Receipt
    receipt_2: Receipt
    tech_cf: str
    tech_vat: str
