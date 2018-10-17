# coding=utf-8
"""definition of portfolio for payoff estimation"""

import numpy as np
from enum import Enum
from instrument import InstType, option_type


class CurveType(Enum):
    """supported curve type for portfolio curve generator"""
    Payoff = 'Payoff'
    Profit = 'Profit'
    PV = 'PV'
    Delta = 'Delta'


class Portfolio(object):
    """
    portfolio class
    can estimate all components total payoff
    """
    def __init__(self, inst_list_):
        self._components = inst_list_
        self._components_show = []
        self._mkt_data = None
        self._engine = None
        self._isp = self._check_isp()
        self._maturity = self._check_maturity()
        self._has_stock = self._check_stock()

    def gen_curve(self, type_, margin_=20, step_=1, full_=False):
        """generate x (spot / ISP) and y (payoff or) for portfolio payoff curve"""
        if type_ == CurveType.Payoff.value:
            _curve_func = self._payoff
        elif type_ == CurveType.Profit.value:
            _curve_func = self._profit
        elif type_ == CurveType.PV.value:
            _curve_func = self._pv
        elif type_ == CurveType.Delta.value:
            _curve_func = self._delta
        else:
            raise ValueError("invalid curve type {}".format(type_))

        _x = self._x_range(margin_, step_)
        _y = [np.vectorize(_curve_func)(_x)]

        if full_:
            if type_ == CurveType.Payoff.value:
                _y.extend([np.array([_inst.payoff(_spot) for _spot in _x]) for _inst in self._components_show])
            elif type_ == CurveType.Profit.value:
                _y.extend([np.array([_inst.profit(_spot) for _spot in _x]) for _inst in self._components_show])
            elif type_ == CurveType.PV.value:
                _y.extend([np.array([_inst.pv(self.mkt_data, self.engine, _spot) * _inst.unit for _spot in _x])
                           for _inst in self._components_show])
            elif type_ == CurveType.Delta.value:
                _y.extend([np.array([_inst.delta(self.mkt_data, self.engine, _spot) * _inst.unit for _spot in _x])
                           for _inst in self._components_show])
        return _x, _y

    def set_show(self, inst_show_):
        """..."""
        self._components_show = list(set(inst_show_) - set(self._components))

    def set_mkt(self, mkt_data_):
        """..."""
        self.mkt_data = mkt_data_

    def set_engine(self, engine_):
        """..."""
        self.engine = engine_

    def isp(self):
        """..."""
        return self._isp

    def maturity(self):
        """..."""
        return self._maturity

    def has_stock(self):
        """..."""
        return self._has_stock

    @property
    def mkt_data(self):
        """market data"""
        if self._mkt_data is None:
            raise ValueError("market data not specified")
        return self._mkt_data

    @mkt_data.setter
    def mkt_data(self, mkt_data_):
        self._mkt_data = mkt_data_

    @property
    def engine(self):
        """pricing engine"""
        if self._engine is None:
            raise ValueError("pricing engine not specified")
        return self._engine

    @engine.setter
    def engine(self, engine_):
        self._engine = engine_

    def _payoff(self, spot_):
        return sum([_comp.payoff(spot_) for _comp in self._components])

    def _profit(self, spot_):
        return sum([_comp.profit(spot_) for _comp in self._components])

    def _pv(self, spot_):
        return sum([_comp.pv(self.mkt_data, self.engine, spot_) * _comp.unit for _comp in self._components])

    def _delta(self, spot_):
        return sum([_comp.delta(self.mkt_data, self.engine, spot_) * _comp.unit for _comp in self._components])

    def _x_range(self, margin_, step_):
        _strike_list = [_comp.strike for _comp in self._components if _comp.type in option_type]
        _min = min(_strike_list) if _strike_list else self._isp
        _max = max(_strike_list) if _strike_list else self._isp
        _dist = max([self._isp - _min, _max - self._isp])
        _x = np.arange(max(self._isp - _dist - margin_, 0), self._isp + _dist + margin_ + step_, step_)
        return _x

    def _check_isp(self):
        _isp = set([_comp.isp for _comp in self._components])
        if len(_isp) > 1:
            raise ValueError("isp of all components should be same")
        return _isp.pop() if len(_isp) == 1 else 100

    def _check_maturity(self):
        _maturity = set([_comp.maturity for _comp in self._components if _comp.type in option_type])
        if len(_maturity) > 1:
            raise ValueError("maturity of all components should be same")
        return _maturity.pop() if len(_maturity) == 1 else 0

    def _check_stock(self):
        return len(list(filter(lambda x: x.type == InstType.Stock.value, self._components))) > 0
