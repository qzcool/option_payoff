# coding=utf-8
"""market and engine parameters"""

from enum import Enum


class EnvParam(Enum):
    """market parameter"""
    RiskFreeRate = 'RiskFreeRate'
    UdVolatility = 'UdVolatility'
    UdConDivRate = 'UdConDivRate'
    CostRounding = 'CostRounding'
    PricingEngine = 'PricingEngine'


class EngineMethod(Enum):
    """engine evaluation method"""
    BS = 'Black-Scholes'
    MC = 'Monte-Carlo'


class EngineParam(Enum):
    """engine parameter"""
    MCIteration = 'MCIteration'
