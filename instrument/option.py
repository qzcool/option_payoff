# coding=utf-8
"""definition of option for payoff estimation and pricing"""

import numpy as np
import scipy.stats as sps
from enum import Enum
from instrument import Instrument, InstParam, InstType
from instrument.parameter import EngineMethod, EngineParam, MktParam


class OptionType(Enum):
    """option type - CALL or PUT"""
    Call = 0
    Put = 1


class Option(Instrument):
    """
    option class with basic parameters
    only vanilla option is available (barrier is not supported)
    can estimate option payoff under different level of spot
    can evaluate option price under different market using different evaluation engine
    """
    _name = "option"
    _callput = None
    _strike = None
    _maturity = None
    _ud_vol = None

    def __init__(self, inst_dict_):
        super(Option, self).__init__(inst_dict_)
        self.callput = inst_dict_.get(InstParam.OptionType.value)
        self.strike = inst_dict_.get(InstParam.OptionStrike.value)
        self.maturity = inst_dict_.get(InstParam.OptionMaturity.value)

    def payoff(self, spot_):
        """get option payoff for given spot"""
        _reference = spot_ - self.strike if self.callput == OptionType.Call.value else self.strike - spot_
        return (max([_reference, 0]) - self.price) * self.unit

    def evaluate(self, mkt_dict_, engine_):
        """do option pricing with market data and engine"""
        _rate, _vol = self._load_market(mkt_dict_)
        _method, _param = self._load_engine(engine_)
        _sign = 1 if self.callput == OptionType.Call.value else -1

        if _method == EngineMethod.Analytic.value:
            _d1 = (np.ma.log(100 / self.strike) + (_rate + _vol ** 2 / 2) * self.maturity) \
                  / _vol / np.ma.sqrt(self.maturity)
            _d2 = _d1 - _vol * np.ma.sqrt(self.maturity)
            return _sign * (100 * sps.norm.cdf(_sign * _d1) -
                            self.strike * np.ma.exp(-_rate * self.maturity) * sps.norm.cdf(_sign * _d2))

        elif _method == EngineMethod.MC.value:
            _iteration = _param.get(EngineParam.MCIteration.value)
            if not _iteration:
                raise ValueError("iteration not specified")
            if not isinstance(_iteration, int):
                raise ValueError("type <int> is required for iteration, not {}".format(type(_iteration)))
            _rand = np.random.normal(0, 1, _iteration)
            _spot = 100 * np.ma.exp((_rate - _vol ** 2 / 2) * self.maturity + _vol * np.ma.sqrt(self.maturity) * _rand)
            _price = [max(_sign * (_s - self.strike), 0) for _s in _spot]
            return np.average(_price) * np.ma.exp(-_rate * self.maturity)

    @property
    def callput(self):
        """option type - CALL or PUT"""
        if self._callput is None:
            raise ValueError("{} type not specified".format(self._name))
        return self._callput

    @callput.setter
    def callput(self, callput_):
        if callput_ not in [_type.value for _type in OptionType]:
            raise ValueError("invalid {} type given".format(self._name))
        self._callput = callput_

    @property
    def strike(self):
        """strike level - percentage of ISP"""
        if self._strike is None:
            raise ValueError("strike level not specified")
        return self._strike

    @strike.setter
    def strike(self, strike_):
        if not isinstance(strike_, float) and not isinstance(strike_, int):
            raise ValueError("type <int> or <float> is required for strike level, not {}".format(type(strike_)))
        self._strike = strike_

    @property
    def maturity(self):
        """option maturity - year"""
        if self._maturity is None:
            raise ValueError("maturity not specified")
        return self._maturity

    @maturity.setter
    def maturity(self, maturity_):
        if maturity_:
            if not isinstance(maturity_, (int, float)):
                raise ValueError("type <int> or <float> is required for maturity, not {}".format(type(maturity_)))
            self._maturity = maturity_

    @staticmethod
    def _load_market(mkt_dict_):
        _rate = mkt_dict_.get(MktParam.RiskFreeRate.value)
        if not isinstance(_rate, (int, float)):
            raise ValueError("type <int> or <float> is required for market risk free rate, not {}".format(type(_rate)))
        _vol = mkt_dict_.get(MktParam.UdVolatility.value)
        if not isinstance(_vol, (int, float)):
            raise ValueError("type <int> or <float> is required for underlying volatility, not {}".format(type(_vol)))
        return _rate / 100, _vol / 100

    @staticmethod
    def _load_engine(engine_):
        _method = engine_.get('engine')
        if _method not in [_m.value for _m in EngineMethod]:
            raise ValueError("invalid evaluation engine given: {}".format(_method))
        _param = engine_.get('param', {})
        return _method, _param


if __name__ == '__main__':
    import sys
    sys.path.append("/Users/Tongyan/Desktop/python_project/")

    from personal_utils.logger_utils import get_default_logger
    from personal_utils.time_utils import Timer

    logger = get_default_logger("option pricing test")

    callput = OptionType.Call.value
    strike = 80
    spot = 100
    maturity = 1
    rate = 2
    vol = 5
    iteration = 1000000

    inst_1 = {
        InstParam.InstType.value: InstType.Option.value,
        InstParam.OptionType.value: callput,
        InstParam.OptionStrike.value: strike,
        InstParam.OptionMaturity.value: maturity
    }

    mkt = {
        MktParam.RiskFreeRate.value: rate,
        MktParam.UdVolatility.value: vol
    }

    engine_1 = dict(engine=EngineMethod.Analytic.value)
    engine_2 = dict(engine=EngineMethod.MC.value, param={EngineParam.MCIteration.value: iteration})

    option_1 = Instrument.get_inst(inst_1)

    _timer = Timer("option pricing: {} {}, {} years, rate {}%, vol {}%".format(
        strike, "call" if callput == OptionType.Call.value else "put", maturity, rate, vol), logger, rounding_=6)
    price_bs = round(option_1.evaluate(mkt, engine_1), 6)
    logger.info("price = {} (Black-Scholes)".format(price_bs))
    _timer.mark("pricing using Black-Scholes")
    price_mc = round(option_1.evaluate(mkt, engine_2), 6)
    logger.info("price = {} (Monte-Carlo, {} iteration)".format(price_mc, iteration))
    _timer.mark("pricing using Monte-Carlo with {} iteration".format(iteration))
    _timer.close()

    option_1.price = price_bs
    option_1.unit = 1
    logger.info("option payoff at spot {}: {}".format(spot, round(option_1.payoff(spot), 6)))
