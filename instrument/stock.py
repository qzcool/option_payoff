# coding=utf-8
"""definition of stock for payoff estimation and pricing"""

from instrument import Instrument


class Stock(Instrument):
    """stock class with basic parameters"""
    _name = "option"

    def payoff(self, spot_):
        """get stock payoff for given spot"""
        return (spot_ - self.price) * self.unit

    def evaluate(self, mkt_dict_, engine_):
        """no evaluation needed"""
        return self.price
