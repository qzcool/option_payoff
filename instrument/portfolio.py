# coding=utf-8
"""definition of portfolio for payoff estimation"""

from copy import deepcopy
from enum import Enum
from instrument import InstType, option_type
from instrument.default_param import env_default_param
from instrument.env_param import EnvParam
from numpy import arange, array, transpose, vectorize


class CurveType(Enum):
    """supported curve type for portfolio curve generator"""
    Payoff = 'Payoff'
    NetPayoff = 'Net Payoff'
    PnL = 'PnL'
    PV = 'PV'
    Delta = 'Delta'
    Gamma = 'Gamma'


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
        self._center = env_default_param[EnvParam.UdSpotForPrice.value]
        self._maturity = self._check_maturity()
        self._has_stock = self._check_stock()
        self._func_map = {
            CurveType.Payoff.value: ('_payoff', 'payoff'),
            CurveType.NetPayoff.value: ('_net_payoff', 'net_payoff'),
            CurveType.PnL.value: ('_pnl', 'pnl'),
            CurveType.PV.value: ('_pv', 'pv'),
            CurveType.Delta.value: ('_delta', 'delta'),
            CurveType.Gamma.value: ('_gamma', 'gamma'),
        }

    def gen_curve(self, type_, margin_=20, step_=1, full_=False):
        """generate x (spot / ISP) and y (payoff or) for portfolio payoff curve"""
        _curve_func = [self.__getattribute__(self._func_map[type_][0])]
        if full_:
            for _comp in self._components_show:
                _curve_func.append(_comp.__getattribute__(self._func_map[type_][1]))

        _x = self._x_range(margin_, step_)
        _y = []
        for _spot in _x:
            _input = deepcopy(self.mkt_data)
            _input[EnvParam.UdSpotForPrice.value] = _spot
            _y .append([_func(_input) for _func in _curve_func])
        _y = transpose(_y)

        # if type_ == CurveType.Payoff.value:
        #     _curve_func = self._payoff
        # elif type_ == CurveType.NetPayoff.value:
        #     _curve_func = self._net_payoff
        # elif type_ == CurveType.PnL.value:
        #     _curve_func = self._pnl
        # elif type_ == CurveType.PV.value:
        #     _curve_func = self._pv
        # elif type_ == CurveType.Delta.value:
        #     _curve_func = self._delta
        # elif type_ == CurveType.Gamma.value:
        #     _curve_func = self._gamma
        # else:
        #     raise ValueError("invalid curve type {}".format(type_))
        #
        # _x = self._x_range(margin_, step_)
        # _y = [vectorize(_curve_func)(_x)]
        #
        # if full_:
        #     if type_ == CurveType.Payoff.value:
        #         _y.extend([array([_inst.payoff(_spot) for _spot in _x]) for _inst in self._components_show])
        #     elif type_ == CurveType.NetPayoff.value:
        #         _y.extend([array([_inst.net_payoff(_spot) for _spot in _x]) for _inst in self._components_show])
        #     elif type_ == CurveType.PnL.value:
        #         _y.extend([array([_inst.pnl(self.mkt_data, self.engine, _spot) for _spot in _x])
        #                    for _inst in self._components_show])
        #     elif type_ == CurveType.PV.value:
        #         _y.extend([array([_inst.pv(self.mkt_data, self.engine, _spot) * _inst.unit for _spot in _x])
        #                    for _inst in self._components_show])
        #     elif type_ == CurveType.Delta.value:
        #         _y.extend([array([_inst.delta(self.mkt_data, self.engine, _spot) * _inst.unit for _spot in _x])
        #                    for _inst in self._components_show])
        #     elif type_ == CurveType.Gamma.value:
        #         _y.extend([array([_inst.gamma(self.mkt_data, self.engine, _spot) * _inst.unit for _spot in _x])
        #                    for _inst in self._components_show])
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

    def maturity(self):
        """..."""
        return self._maturity

    def center(self):
        """..."""
        return self._center

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

    def _payoff(self, mkt_data_):
        return sum([_comp.payoff(mkt_data_) for _comp in self._components])

    def _net_payoff(self, mkt_data_):
        return sum([_comp.net_payoff(mkt_data_) for _comp in self._components])

    def _pnl(self, mkt_data_):
        return sum([_comp.pnl(mkt_data_, self.engine) for _comp in self._components])

    def _pv(self, mkt_data_):
        return sum([_comp.pv(mkt_data_, self.engine) * _comp.unit for _comp in self._components])

    def _delta(self, mkt_data_):
        return sum([_comp.delta(mkt_data_, self.engine) * _comp.unit for _comp in self._components])

    def _gamma(self, mkt_data_):
        return sum([_comp.gamma(mkt_data_, self.engine) * _comp.unit for _comp in self._components])

    def _x_range(self, margin_, step_):
        _strike_list = [_comp.strike for _comp in self._components if _comp.type in option_type]
        _min = min(_strike_list) if _strike_list else self._center
        _max = max(_strike_list) if _strike_list else self._center
        _dist = max([self._center - _min, _max - self._center])
        _x = arange(max(self._center - _dist - margin_, 0), self._center + _dist + margin_ + step_, step_)
        return _x

    def _check_maturity(self):
        _maturity = set([_comp.maturity for _comp in self._components if _comp.type in option_type])
        if len(_maturity) > 1:
            raise ValueError("maturity of all components should be same")
        return _maturity.pop() if len(_maturity) == 1 else 0

    def _check_stock(self):
        return len(list(filter(lambda x: x.type == InstType.Stock.value, self._components))) > 0
