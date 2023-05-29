from src.fp import FP
import logging


# Set the system logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)


def test_fp():
    fp = FP(
        categories=[],
        plus=[],
        ivas=[],
        payments=[],
        headers=[],
    )
    logger.debug(fp)
    assert isinstance(fp, FP)


if __name__ == '__main__':
    test_fp()
    from tests.unit.test_iva import test_iva_aliquota
    test_iva_aliquota()
