# coding=utf-8
"""definition of portfolio for payoff estimation"""

import numpy as np
from instrument import option_type
from instrument.parameter import EnvParam
from utils import to_continuous_rate


class Portfolio(object):
    """
    portfolio class
    can estimate all components total payoff
    """
    def __init__(self, inst_list_):
        self._components = inst_list_

    def payoff_curve(self, margin_=20, step_=1):
        """generate x (spot / ISP) and y (payoff) for portfolio payoff curve"""
        _min, _max = self._x_range()
        _dist = max([100 - _min, _max - 100])
        _x = np.arange(100 - _dist - margin_, 100 + _dist + margin_ + step_, step_)
        _y = np.vectorize(self._payoff)(_x)
        return _x, _y

    def yield_curve(self, mkt_data_, margin_=20, step_=1):
        """generate x (spot / ISP) and y (return or yield ratio) for portfolio payoff curve"""
        _maturity = self._check_maturity()
        _x, _payoff = self.payoff_curve(margin_, step_)
        _cost = self._cost()
        _rate = to_continuous_rate(mkt_data_[EnvParam.RiskFreeRate.value] / 100)
        _payoff = _payoff * np.ma.exp(-_rate * _maturity) if _maturity else _payoff
        _y = _payoff - _cost
        return _x, _y

    def _x_range(self):
        _strike_list = [_comp.strike for _comp in self._components if _comp.type in option_type]
        _min = min(_strike_list) if _strike_list else 100
        _max = max(_strike_list) if _strike_list else 100
        return _min, _max

    def _payoff(self, spot_):
        return sum([_comp.payoff(spot_) for _comp in self._components])

    def _cost(self):
        return sum([_comp.price for _comp in self._components])

    def _check_maturity(self):
        _maturity = set([_comp.maturity for _comp in self._components if _comp.type in option_type])
        if len(_maturity) > 1:
            raise ValueError("maturity of all components should be same")
        return _maturity.pop() if len(_maturity) == 1 else None
