# coding=utf-8
"""definition of base instrument"""

from enum import Enum


class InstParam(Enum):
    """instrument parameters"""
    InstID = 'InstID'
    InstType = 'InstType'
    InstUnit = 'InstUnit'
    InstPrice = 'InstPrice'
    OptionType = 'OptionType'
    OptionStrike = 'OptionStrike'
    OptionMaturity = 'OptionMaturity'


class InstType(Enum):
    """instrument type"""
    CallOption = 'CALL'
    PutOption = 'PUT'


option_type = [InstType.CallOption.value, InstType.PutOption.value]


class Instrument(object):
    """
    financial instrument class
    use class method - get_inst to get correct type of instrument
    """
    _name = "instrument"
    _inst_dict = None
    _type = None
    _unit = None
    _price = None

    def __init__(self, inst_dict_):
        self._inst_dict = inst_dict_
        self.type = inst_dict_.get(InstParam.InstType.value)
        self.unit = inst_dict_.get(InstParam.InstUnit.value)
        self.price = inst_dict_.get(InstParam.InstPrice.value)

    @classmethod
    def get_inst(cls, inst_dict_):
        """get instrument through instrument dictionary"""
        type_ = inst_dict_.get(InstParam.InstType.value)
        if type_ in option_type:
            from instrument.option import Option
            return Option(inst_dict_)
        if type_ is None:
            raise ValueError("instrument type not specified")

    def payoff(self, spot_):
        """get instrument payoff for given spot"""
        raise NotImplementedError

    def evaluate(self, mkt_dict_, engine_):
        """evaluate instrument price on given market"""
        raise NotImplementedError

    @property
    def type(self):
        """instrument type"""
        if self._type is None:
            raise ValueError("{} type not specified".format(self._name))
        return self._type

    @type.setter
    def type(self, type_):
        if type_ not in [_type.value for _type in InstType]:
            raise ValueError("invalid {} type given".format(self._name))
        self._type = type_

    @property
    def unit(self):
        """instrument unit - number of instrument"""
        if self._unit is None:
            raise ValueError("{} unit not specified".format(self._name))
        return self._unit

    @unit.setter
    def unit(self, unit_):
        if unit_:
            if not isinstance(unit_, (int, float)):
                raise ValueError("type <int> is required for unit, not {}".format(type(unit_)))
            self._unit = unit_

    @property
    def price(self):
        """instrument price - percentage of ISP"""
        if self._price is None:
            raise ValueError("{} price not specified".format(self._name))
        return self._price

    @price.setter
    def price(self, price_):
        if price_:
            if not isinstance(price_, (int, float)):
                raise ValueError("type <int> or <float> is required for price, not {}".format(type(price_)))
            self._price = price_
