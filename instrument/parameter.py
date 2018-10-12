# coding=utf-8
"""market and engine parameters"""

from enum import Enum


class MktParam(Enum):
    """market parameter"""
    RiskFreeRate = 'RiskFreeRate'
    UdVolatility = 'UdVolatility'


class EngineMethod(Enum):
    """engine evaluation method"""
    Analytic = 'Analytic'
    MC = 'MC'


class EngineParam(Enum):
    """engine parameter"""
    MCIteration = 'MCIteration'
