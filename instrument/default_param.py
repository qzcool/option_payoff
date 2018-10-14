# coding=utf-8
"""dafault value of all parameters"""

from instrument import InstParam, InstType
from instrument.parameter import EnvParam, EngineMethod, EngineParam


default_param = {
    InstType.CallOption.value: {
        InstParam.InstUnit.value: 1,
        InstParam.InstCost.value: 0,
        InstParam.OptionMaturity.value: 1,
        InstParam.OptionStrike.value: 100
    },
    InstType.PutOption.value: {
        InstParam.InstUnit.value: 1,
        InstParam.InstCost.value: 0,
        InstParam.OptionMaturity.value: 1,
        InstParam.OptionStrike.value: 100
    },
    InstType.Stock.value: {
        InstParam.InstUnit.value: 1
    }
}

default_type = InstType.CallOption.value

env_default_param = {
    EnvParam.RiskFreeRate.value: 3,
    EnvParam.UdVolatility.value: 5,
    EnvParam.UdDivYieldRatio.value: 0,
    EnvParam.CostRounding.value: 2,
    EnvParam.PricingEngine.value: {
        'engine': EngineMethod.BS.value,
        'param': {
            EngineParam.MCIteration.value: 1000000
        }
    }
}
