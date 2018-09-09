# coding=utf-8
"""definition of option and option portfolio, can estimate payoff directly"""

import numpy as np

valid_direction = ['LONG', 'SHORT']
valid_option_type = ['CALL', 'PUT']
valid_stock_type = 'STOCK'


class Instrument(object):
    """..."""
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
    def get_inst(cls, type_, **kwargs):
        """..."""
        if type_ == valid_stock_type:
            return Stock(**kwargs)
        elif type_ in valid_option_type:
            return Option(type_, **kwargs)

    def payoff(self, spot_):
        """..."""
        raise NotImplementedError

    @property
    def type(self):
        """option type - CALL or PUT"""
        if not self._type:
            raise ValueError("Option type has not been set")
        return self._type

    @type.setter
    def type(self, type_):
        if not isinstance(type_, str):
            raise ValueError("Type <str> is required for option type, not {}".format(type(type_)))
        self._type = type_.upper()

    @property
    def direction(self):
        """option direction - LONG or SHORT"""
        if not self._direction:
            raise ValueError("Option direction has not been set")
        return self._direction

    @direction.setter
    def direction(self, direction_):
        if not isinstance(direction_, str):
            raise ValueError("Type <str> is required for option direction, not {}".format(type(direction_)))
        if direction_.upper() not in valid_direction:
            raise ValueError("Invalid option direction {}".format(direction_.upper()))
        self._direction = direction_

    @property
    def price(self):
        """option price - percentage of buy spot"""
        if self._price is None:
            raise ValueError("Option price has not been set")
        return self._price

    @price.setter
    def price(self, price_):
        if not isinstance(price_, float) and not isinstance(price_, int):
            raise ValueError("Type <int> or <float> is required for option price, not {}".format(type(price_)))
        self._price = price_

    @property
    def unit(self):
        """option unit - number of option"""
        if self._unit is None:
            raise ValueError("Option unit has not been set")
        return self._unit

    @unit.setter
    def unit(self, unit_):
        if not isinstance(unit_, int):
            raise ValueError("Type <int> is required for option price, not {}".format(type(unit_)))
        self._unit = unit_


class Option(Instrument):
    """
        option class with basic parameters
        only vanilla option is available (barrier is not supported)
        can estimate option payoff under different level of spot
    """

    _strike = None

    def __init__(self, type_, direction_, strike_, price_=0, unit_=1, *args, **kwargs):
        super(Option, self).__init__(type_, direction_, price_, unit_)
        self.strike = strike_

    def payoff(self, spot_):
        """get option payoff for given spot"""
        _reference = spot_ - self.strike if self.type == 'CALL' else self.strike - spot_
        _signal = 1 if self.direction == 'LONG' else -1
        return _signal * (max([_reference, 0]) - self.price) * self.unit

    @property
    def type(self):
        """option type - CALL or PUT"""
        if not self._type:
            raise ValueError("Option type has not been set")
        return self._type

    @type.setter
    def type(self, type_):
        if not isinstance(type_, str):
            raise ValueError("Type <str> is required for option type, not {}".format(type(type_)))
        if type_.upper() not in valid_option_type:
            raise ValueError("Invalid option type {}".format(type_.upper()))
        self._type = type_.upper()

    @property
    def strike(self):
        """strike level - percentage of buy spot"""
        if self._strike is None:
            raise ValueError("Strike level has not been set")
        return self._strike

    @strike.setter
    def strike(self, strike_):
        if not isinstance(strike_, float) and not isinstance(strike_, int):
            raise ValueError("Type <int> or <float> is required for strike level, not {}".format(type(strike_)))
        self._strike = strike_


class Stock(Instrument):
    """..."""
    def __init__(self, direction_, price_=100, unit_=1, *args, **kwargs):
        _type = valid_stock_type
        super(Stock, self).__init__(_type, direction_, price_, unit_)

    def payoff(self, spot_):
        """..."""
        return (spot_ - self.price) * self.unit


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
        _x = np.arange(100 - _dist - margin_, 100 + _dist + margin_, step_)
        _y = np.vectorize(self._payoff)(_x)
        return _x, _y

    def _payoff(self, spot_):
        return sum([_comp.payoff(spot_) for _comp in self._components])


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    option_a = Option('CALL', 'BUY', 80)
    option_b = Option('CALL', 'SELL', 120)
    portfolio = OptionPortfolio([option_a, option_b])
    x, y = portfolio.payoff_curve()
    plt.plot(x, y, 'r')
    plt.show()
