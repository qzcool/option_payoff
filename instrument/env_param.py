# coding=utf-8
"""market and engine parameters"""

from copy import deepcopy
from enum import Enum


class EnvParam(Enum):
    """market parameter"""
    RiskFreeRate = 'RiskFreeRate'
    UdVolatility = 'UdVolatility'
    UdDivYieldRatio = 'UdDivYieldRatio'
    UdInitialPrice = 'UdInitialPrice'
    PortMaturity = 'PortMaturity'
    CostRounding = 'CostRounding'
    PricingEngine = 'PricingEngine'


class EngineMethod(Enum):
    """engine evaluation method"""
    BS = 'Black-Scholes'
    MC = 'Monte-Carlo'


class EngineParam(Enum):
    """engine parameter"""
    MCIteration = 'MCIteration'


def parse_env(env_param_):
    """..."""
    _mkt = deepcopy(env_param_)
    _engine = _mkt.pop(EnvParam.PricingEngine.value)
    _rounding = _mkt.pop(EnvParam.CostRounding.value)
    return _mkt, _engine, _rounding
