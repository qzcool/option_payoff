# coding=utf-8
"""pricing env dialog"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QButtonGroup, QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QVBoxLayout, QLineEdit
from enum import Enum
from gui.custom import CustomRadioButton
from instrument.parameter import EngineMethod, EngineParam, EnvParam
from utils import float_int


class FieldType(Enum):
    """Field type"""
    String = 0
    Number = 1
    Radio = 2


fixed_width = 180

env_param = [
    (FieldType.Number.value, EnvParam.RiskFreeRate.value, "Discrete Risk Free Rate (%):", fixed_width, None),
    (FieldType.Number.value, EnvParam.UdVolatility.value, "Ud Volatility (%):", fixed_width, None),
    (FieldType.Number.value, EnvParam.UdConDivRate.value, "Ud Con. Dividend Rate (%):", fixed_width, None),
    (FieldType.Number.value, EnvParam.CostRounding.value, "Instrument Cost Rounding:", fixed_width, None),
    (FieldType.Radio.value, EnvParam.PricingEngine.value, "Instrument Pricing Engine:", fixed_width, None)
]

engine_param = [
    (FieldType.Number.value, EngineParam.MCIteration.value, "Monte-Carlo Iterations:", fixed_width,
     EngineMethod.MC.value),
]


class PricingEnv(QDialog):
    """
    dialog for editing pricing environment parameters
    included paramters should be all defined above - env_param
    """
    def __init__(self, parent_, *args, **kwargs):
        super(PricingEnv, self).__init__(*args, **kwargs)
        self._parent = parent_
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("Pricing Env")
        # initialize basic widgets
        self._main_layout = QVBoxLayout(self)
        # setup and show
        self.setup_ui()
        self.setLayout(self._main_layout)
        self.show()

    def setup_ui(self):
        """setup all parameter input widget and buttons"""
        for _param in env_param:
            if _param[1] == EnvParam.PricingEngine.value:
                self._add_param(_param, self._parent.env_data[EnvParam.PricingEngine.value]['engine'],
                                dict(range=[_engine.value for _engine in EngineMethod], param=engine_param,
                                     default=self._parent.env_data[EnvParam.PricingEngine.value]['param']))
            else:
                self._add_param(_param, self._parent.env_data[_param[1]])
        _btn = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        _btn.button(QDialogButtonBox.Ok).setDefault(True)
        _btn.accepted.connect(self._on_ok)
        _btn.rejected.connect(self.reject)
        self._main_layout.addWidget(_btn)

    def _add_param(self, param_, default_=None, supplement_=None):
        if param_[0] in [FieldType.String.value, FieldType.Number.value]:
            _hbox = QHBoxLayout()
            _label = QLabel(param_[2])
            _label.setFixedWidth(param_[3])
            _hbox.addWidget(_label)
            _wgt = QLineEdit(self)
            _wgt.setAlignment(Qt.AlignRight)
            if default_ is not None:
                _wgt.setText(str(default_))
            self.__setattr__(param_[1], _wgt)
            _hbox.addWidget(_wgt)
            self._main_layout.addLayout(_hbox)

            if param_[4] is not None:
                try:
                    _parent = self.__getattribute__(param_[4])
                    if not hasattr(_parent, 'param'):
                        _parent.__setattr__('param', [])
                    _parent.param.append(param_[1])
                    _parent.__setattr__(param_[1], _wgt)
                    _wgt.setEnabled(_parent.isChecked())
                except AttributeError:
                    pass

        elif param_[0] == FieldType.Radio.value and isinstance(supplement_, dict):
            _vbox = QVBoxLayout()
            _label = QLabel(param_[2])
            _label.setFixedWidth(param_[3])
            _vbox.addWidget(_label)
            _hbox = QHBoxLayout()
            _btn_group = QButtonGroup()
            self.__setattr__(param_[1], _btn_group)
            _range = supplement_.get('range', [])
            _param = supplement_.get('param', [])
            _default = supplement_.get('default', [])
            for _idx, _item in enumerate(_range):
                _wgt = CustomRadioButton(_item, _item, self)
                self.__setattr__(_item, _wgt)
                _hbox.addWidget(_wgt)
                _btn_group.addButton(_wgt, _idx)
            _vbox.addLayout(_hbox)
            self._main_layout.addLayout(_vbox)
            self.__getattribute__(default_).setChecked(True)
            if _param:
                for _p in _param:
                    self._add_param(_p, _default.get(_p[1]) if default_ else None)
                for _item in _range:
                    _wgt = self.__getattribute__(_item)
                    if hasattr(_wgt, 'param'):
                        _wgt.changed.connect(self._radio_connection)

    def _radio_connection(self, wgt_name_):
        _wgt = self.__getattribute__(wgt_name_)
        for _param in _wgt.param:
            _child = _wgt.__getattribute__(_param)
            _child.setEnabled(_wgt.isChecked())

    def _on_ok(self):
        _env = dict()
        for _param in env_param:
            if _param[1] == EnvParam.PricingEngine.value:
                _engine = dict()
                _engine['engine'] = [_e.value for _e in EngineMethod][self.__getattribute__(_param[1]).checkedId()]
                _engine['param'] = dict()
                for _p in engine_param:
                    _engine['param'][_p[1]] = self._get_wgt_value(_p[1], _p[0])
                _env[_param[1]] = _engine
            else:
                _env[_param[1]] = self._get_wgt_value(_param[1], _param[0])
        self._parent.env_data = _env
        self.accept()

    def _get_wgt_value(self, wgt_name_, wgt_type_):
        _wgt = self.__getattribute__(wgt_name_)
        if wgt_type_ == FieldType.String.value:
            return _wgt.text()
        elif wgt_type_ == FieldType.Number.value:
            return float_int(_wgt.text())
        elif wgt_type_ == FieldType.Radio.value:
            return _wgt.checkedId()
        else:
            return None
