from src.fp import FP


def test_fp():
    fp = FP(
        categories=[],
        plus=[],
        ivas=[],
        payments=[],
        headers=[],
    )
    assert isinstance(fp, FP)

