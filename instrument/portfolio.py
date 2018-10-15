# coding=utf-8
"""definition of portfolio for payoff estimation"""

import numpy as np
from instrument import option_type
from instrument.env_param import EnvParam
from utils import to_continuous_rate


class Portfolio(object):
    """
    portfolio class
    can estimate all components total payoff
    """
    def __init__(self, inst_list_):
        self._components = inst_list_
        self._components_show = []
        self._mkt_data = None

    def payoff_curve(self, margin_=20, step_=1, full_=False):
        """generate x (spot / ISP) and y (payoff) for portfolio payoff curve"""
        def _payoff(spot_):
            return sum([_comp.payoff(spot_) for _comp in self._components])

        _x = self._x_range(margin_, step_)
        _y = [np.vectorize(_payoff)(_x)]

        if full_:
            for _inst in self._components_show:
                _y.insert(0, np.array([_inst.payoff(_spot) for _spot in _x]))
        return _x, _y

    def yield_curve(self, margin_=20, step_=1, full_=False):
        """generate x (spot / ISP) and y (return or yield ratio) for portfolio payoff curve"""
        _rate = to_continuous_rate(self.mkt_data[EnvParam.RiskFreeRate.value] / 100)
        _maturity = self._check_maturity()

        def _yield(spot_):
            return sum([_comp.yield_t0(spot_, _rate, _maturity) for _comp in self._components])

        _x = self._x_range(margin_, step_)
        _y = [np.vectorize(_yield)(_x)]

        if full_:
            for _inst in self._components_show:
                _y.insert(0, np.array([_inst.yield_t0(_spot, _rate, _maturity) for _spot in _x]))
        return _x, _y

    def set_show(self, inst_show_):
        """..."""
        self._components_show = list(set(inst_show_) - set(self._components))

    def set_mkt(self, mkt_data_):
        """..."""
        self.mkt_data = mkt_data_

    @property
    def mkt_data(self):
        """market data"""
        if self._mkt_data is None:
            raise ValueError("market data not specified")
        return self._mkt_data

    @mkt_data.setter
    def mkt_data(self, mkt_data_):
        self._mkt_data = mkt_data_

    def _x_range(self, margin_, step_):
        _strike_list = [_comp.strike for _comp in self._components if _comp.type in option_type]
        _min = min(_strike_list) if _strike_list else 100
        _max = max(_strike_list) if _strike_list else 100
        _dist = max([100 - _min, _max - 100])
        _x = np.arange(100 - _dist - margin_, 100 + _dist + margin_ + step_, step_)
        return _x

    def _check_maturity(self):
        _maturity = set([_comp.maturity for _comp in self._components if _comp.type in option_type])
        if len(_maturity) > 1:
            raise ValueError("maturity of all components should be same")
        return _maturity.pop() if len(_maturity) == 1 else 0
