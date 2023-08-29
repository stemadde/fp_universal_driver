from src.Prod96.command import Command, Receipt


def test_receipt():
    receipt = Receipt(
        ip='192.168.1.69',
        port=9100,
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
        ],
    )
    assert isinstance(receipt, Receipt)
