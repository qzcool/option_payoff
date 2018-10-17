# coding=utf-8
"""Monte-Carlo engine"""

import numpy as np
from utils import parse_kwargs


class MonteCarlo(object):
    """..."""

    @classmethod
    def stock_price(cls, iteration_=1, **kwargs):
        """generate stock spot through stochastic process"""
        _rand = np.random.normal(0, 1, iteration_)
        _isp, _rate, _div, _vol, _t = parse_kwargs(kwargs, ['isp', 'rate', 'div', 'vol', 'maturity'], 0)
        return _isp * np.ma.exp((_rate - _div - _vol ** 2 / 2) * _t + _vol * np.ma.sqrt(_t) * _rand)
