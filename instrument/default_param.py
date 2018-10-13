# coding=utf-8
"""..."""

from instrument import InstParam, InstType
from instrument.parameter import MktParam


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
    }
}

default_type = InstType.CallOption.value

mkt_ud_default_param = {
    MktParam.RiskFreeRate: 3,
    MktParam.UdVolatility: 5
}
