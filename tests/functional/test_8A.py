from src.Prod8A.fp import FP
from .fp_tests import correct_fp_config, wrong_id_references


def test_std_fp():
    fp = correct_fp_config(FP, ip='192.168.1.76', port=9101)
    assert isinstance(fp, FP)
    wrong_id_references(FP)

    fp.read_from_fp()

    # Test conversion from 8A FP to StdFP
    std_fp = fp.to_fp()
    # Test conversion from std_fp to 8A FP
    new_fp = FP().from_fp(std_fp)

    assert fp == new_fp

    print(fp.ivas)
