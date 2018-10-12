# coding=utf-8
"""definition of portfolio for payoff estimation"""

import numpy as np
from instrument import InstType


class Portfolio(object):
    """
    portfolio class
    can estimate all components total payoff
    """
    def __init__(self, inst_list_):
        self._components = inst_list_

    def payoff_curve(self, margin_=20, step_=1):
        """generate x (spot) and y (payoff) for portfolio payoff curve"""
        _min, _max = self._x_range()
        _dist = max([100 - _min, _max - 100])
        _x = np.arange(100 - _dist - margin_, 100 + _dist + margin_ + step_, step_)
        _y = np.vectorize(self._payoff)(_x)
        return _x, _y

    def _x_range(self):
        _strike_list = [_comp.strike for _comp in self._components if _comp.type == InstType.OPTION.value]
        _min = min(_strike_list) if _strike_list else 100
        _max = max(_strike_list) if _strike_list else 100
        return _min, _max

    def _payoff(self, spot_):
        return sum([_comp.payoff(spot_) for _comp in self._components])
