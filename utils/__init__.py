# coding=utf-8
"""common utility functions"""


def float_int(string_):
    """convert string to int or float according to its real feature"""
    _number = float(string_)
    return _number if _number % 1 else int(_number)
