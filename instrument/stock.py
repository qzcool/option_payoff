# coding=utf-8
"""definition of stock for payoff estimation and pricing"""

from instrument import Instrument


class Stock(Instrument):
    """stock class with basic parameters"""
    _name = "stock"

    def __init__(self, inst_dict_):
        super(Stock, self).__init__(inst_dict_)
        self.price = 100

    def payoff(self, spot_):
        """get stock payoff for given spot"""
        return spot_ * self.unit

    def evaluate(self, mkt_dict_, engine_):
        """no evaluation needed"""
        return self.price
