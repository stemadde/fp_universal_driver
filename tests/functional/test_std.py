from src.fp import FP
from .fp_tests import correct_fp_config, wrong_id_references


def test_std_fp():
    correct_fp_config(FP)
    wrong_id_references(FP)
