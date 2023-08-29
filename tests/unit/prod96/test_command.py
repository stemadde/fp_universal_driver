from src.Prod96.fp import FP


def test_receipt():
    fp = FP(
        ip='192.168.1.69',
        port=9100,
        categories=[],
        plus=[],
        ivas=[],
        payments=[],
        headers=[],
        poses=[],
        protocol='tcp'
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
