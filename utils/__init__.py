# coding=utf-8
"""common utility functions"""

import numpy as np

PRECISION_ZERO = 10 ** -3


def float_int(string_):
    """convert string to int or float according to its real feature"""
    try:
        _number = float(string_)
        return _number if _number % 1 else int(_number)
    except ValueError:
        return None


def to_continuous_rate(rate_):
    """shift discrete rate to continuous rate"""
    return np.ma.log(1 + rate_)
