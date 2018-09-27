# coding=utf-8
"""definition of option and option portfolio, can estimate payoff directly"""

import numpy as np
from enum import Enum


class InstrumentType(Enum):
    """valid instrument type"""
    CALL = 0
    PUT = 1
    STOCK = 2


class TransactionDirection(Enum):
    """valid transaction direction"""
    LONG = 0
    SHORT = 1


valid_option_type = [InstrumentType.CALL, InstrumentType.PUT]


class Instrument(object):
    """financial instrument"""
    _name = 'instrument'
    _type = None
    _direction = None
    _unit = None
    _price = None

    def __init__(self, type_, direction_, price_, unit_=1):
        self.type = type_
        self.direction = direction_
        self.unit = unit_
        self.price = price_

    @classmethod
    def get_inst(cls, type_, direction_, price_, unit_, **kwargs):
        """get instrument through type"""
        if type_ == InstrumentType.STOCK:
            return Stock(direction_=direction_, price_=price_, unit_=unit_)
        elif type_ in valid_option_type:
            return Option(type_=type_, direction_=direction_, price_=price_, unit_=unit_, **kwargs)

    def payoff(self, spot_):
        """get instrument payoff for given spot"""
        raise NotImplementedError

    @property
    def type(self):
        """instrument type"""
        if not self._type:
            raise ValueError("{} type has not been set".format(self._name))
        return self._type

    @type.setter
    def type(self, type_):
        if type_ not in InstrumentType:
            raise ValueError("invalid {} type {}".format(self._name, type_))
        self._type = type_

    @property
    def direction(self):
        """transaction direction"""
        if not self._direction:
            raise ValueError("transaction direction has not been set")
        return self._direction

    @direction.setter
    def direction(self, direction_):
        if direction_ not in TransactionDirection:
            raise ValueError("invalid transaction direction {}".format(direction_))
        self._direction = direction_

    @property
    def price(self):
        """instrument price - percentage of ISP"""
        if self._price is None:
            raise ValueError("{} price has not been set".format(self._name))
        return self._price

    @price.setter
    def price(self, price_):
        if not isinstance(price_, (int, float)):
            raise ValueError("type <int> or <float> is required for {} price, not {}".format(self._name, type(price_)))
        self._price = price_

    @property
    def unit(self):
        """instrument unit - number of instrument"""
        if self._unit is None:
            raise ValueError("{} unit has not been set".format(self._name))
        return self._unit

    @unit.setter
    def unit(self, unit_):
        if not isinstance(unit_, (int, float)):
            raise ValueError("type <int> is required for {} price, not {}".format(self._name, type(unit_)))
        if unit_ < 0:
            raise ValueError("{} unit should not be negative".format(self._name))
        self._unit = unit_


class Option(Instrument):
    """
    option class with basic parameters
    only vanilla option is available (barrier is not supported)
    can estimate option payoff under different level of spot
    """
    _name = 'option'
    _strike = None

    def __init__(self, type_, direction_, price_=0, unit_=1, **kwargs):
        super(Option, self).__init__(type_, direction_, price_, unit_)
        self.strike = kwargs.get('strike_', 100)

    def payoff(self, spot_):
        """get option payoff for given spot"""
        _reference = spot_ - self.strike if self.type == InstrumentType.CALL else self.strike - spot_
        _signal = 1 if self.direction == TransactionDirection.LONG else -1
        return _signal * (max([_reference, 0]) - self.price) * self.unit

    @property
    def type(self):
        """option type - CALL or PUT"""
        if not self._type:
            raise ValueError("{} type has not been set".format(self._name))
        return self._type

    @type.setter
    def type(self, type_):
        if type_ not in valid_option_type:
            raise ValueError("invalid {} type {}".format(self._name, type_))
        self._type = type_

    @property
    def strike(self):
        """strike level - percentage of ISP"""
        if self._strike is None:
            raise ValueError("strike level has not been set")
        return self._strike

    @strike.setter
    def strike(self, strike_):
        if not isinstance(strike_, float) and not isinstance(strike_, int):
            raise ValueError("type <int> or <float> is required for strike level, not {}".format(type(strike_)))
        self._strike = strike_


class Stock(Instrument):
    """stock class with basic parameters"""
    def __init__(self, direction_, price_=100, unit_=1):
        _type = InstrumentType.STOCK
        super(Stock, self).__init__(_type, direction_, price_, unit_)

    def payoff(self, spot_):
        """get stock payoff for given spot"""
        _signal = 1 if self.direction == TransactionDirection.LONG else -1
        return _signal * (spot_ - self.price) * self.unit


class OptionPortfolio(object):
    """
    option portfolio class
    can estimate all components total payoff
    """
    def __init__(self, option_list_):
        self._components = option_list_

    def strike_range(self):
        """return min strike level and max strike level"""
        _strike_list = [_comp.strike for _comp in self._components if _comp.type in valid_option_type]
        _min = min(_strike_list) if _strike_list else 100
        _max = max(_strike_list) if _strike_list else 100
        return _min, _max

    def payoff_curve(self, margin_=20, step_=1):
        """generate x (spot) and y (payoff) for portfolio payoff curve"""
        _min, _max = self.strike_range()
        _dist = max([100 - _min, _max - 100])
        _x = np.arange(100 - _dist - margin_, 100 + _dist + margin_ + step_, step_)
        _y = np.vectorize(self._payoff)(_x)
        return _x, _y

    def _payoff(self, spot_):
        return sum([_comp.payoff(spot_) for _comp in self._components])


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    option_a = Option(InstrumentType.CALL, TransactionDirection.LONG, strike_=80)
    option_b = Option(InstrumentType.CALL, TransactionDirection.SHORT, strike_=120)
    portfolio = OptionPortfolio([option_a, option_b])
    x, y = portfolio.payoff_curve()
    plt.plot(x, y, 'r')
    plt.show()
