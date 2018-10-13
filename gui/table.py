# coding=utf-8
"""instrument table template"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView, QMessageBox, QTableWidgetItem
from copy import deepcopy
from enum import Enum
from gui.custom import CustomComboBox, CustomTableWidget
from instrument import InstType, InstParam, Instrument
from instrument.default_param import default_param, default_type
from instrument.parameter import EnvParam
from utils import float_int


class TableCol(Enum):
    """table column"""
    Type = 'Type'
    Strike = 'Strike'
    Maturity = 'Maturity'
    Unit = 'Unit'
    Cost = 'Cost'


class ColType(Enum):
    """column type"""
    String = 0
    Number = 1
    Other = 2


table_col = [
    (TableCol.Type.value, ColType.Other.value, InstParam.InstType.value, 80),
    (TableCol.Strike.value, ColType.Number.value, InstParam.OptionStrike.value, 50),
    (TableCol.Maturity.value, ColType.Number.value, InstParam.OptionMaturity.value, 50),
    (TableCol.Unit.value, ColType.Number.value, InstParam.InstUnit.value, 50),
    (TableCol.Cost.value, ColType.Number.value, InstParam.InstCost.value, 50),
]


class InstTable(CustomTableWidget):
    """
    instrument table widget to edit instrument info
    all table columns should be defined above - table_col
    """
    _seq = 0

    def __init__(self, parent_, *args, **kwargs):
        super(InstTable, self).__init__(0, len(table_col), *args, **kwargs)
        self._parent = parent_
        self.setHorizontalHeaderLabels([_col[0] for _col in table_col])
        for _idx, _col in enumerate(table_col):
            self.setColumnWidth(_idx, _col[3])
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.rightClicked.connect(self._price)

    def _inst_id(self):
        self._seq += 1
        return "Inst-{}".format(self._seq)

    def add_row(self, data_=None):
        """add a new instrument with given or default data"""
        self.setRowCount(self.rowCount() + 1)
        _id = self._inst_id()
        _type = data_.get(InstParam.InstType.value, default_type) if data_ else default_type

        for _idx, _col in enumerate(table_col):
            if _col[1] in [ColType.String.value, ColType.Number.value]:
                _content = data_.get(_col[2], default_param[_type][_col[2]]) if data_ else default_param[_type][_col[2]]
                _wgt = QTableWidgetItem(str(_content))
                _wgt.setTextAlignment(Qt.AlignCenter)
                self.setItem(self.rowCount() - 1, _idx, _wgt)

            elif _col[1] == ColType.Other.value:
                if _col[0] == TableCol.Type.value:
                    _wgt_name = '{}_type'.format(_id)
                    _wgt = QTableWidgetItem(_wgt_name)
                    _wgt._wgt = CustomComboBox(wgt_name_=_wgt_name)
                    for _inst_type in [_t.value for _t in InstType]:
                        _wgt._wgt.addItem(_inst_type)
                    _wgt._wgt.setCurrentText(_type)
                    _wgt._wgt.setFixedWidth(_col[3])
                    self.__setattr__(_wgt_name, _wgt._wgt)
                    _wgt._wgt.changed.connect(self._set_default)
                    _wgt.setTextAlignment(Qt.AlignCenter)
                    self.setItem(self.rowCount() - 1, _idx, _wgt)
                    self.setCellWidget(self.rowCount() - 1, _idx, _wgt._wgt)
                else:
                    raise ValueError("invalid table column '{}'".format(_col[0]))

            else:
                raise ValueError("invalid column type '{}'".format(_col[1]))

    def copy_row(self):
        """copy an existing instrument and create a new one"""
        self.add_row()
        _row = self.currentRow()
        _raw_data = self._collect_row(_row)

        for _idx, _col in enumerate(table_col):
            if _col[1] in [ColType.String.value, ColType.Number.value]:
                self.item(self.rowCount() - 1, _idx).setText(str(_raw_data[_col[2]]))

            elif _col[1] == ColType.Other.value:
                if _col[0] == TableCol.Type.value:
                    self.__getattribute__(
                        self.item(self.rowCount() - 1, _idx).text()).setCurrentText(_raw_data[_col[2]])

    def delete_row(self):
        """delete an instrument"""
        if self.rowCount() == 1:
            QMessageBox.information(self, "Warning", "Only one option left, cannot be deleted.")
        else:
            _row = self.currentRow()
            self.removeRow(_row)

    def collect(self):
        """collect all instruments data"""
        return [self._collect_row(_row) for _row in range(self.rowCount())]

    def _collect_row(self, row_):
        _data_dict = dict()
        for _idx, _col in enumerate(table_col):
            if _col[1] == ColType.String.value:
                _data = self.item(row_, _idx).text()
                _data_dict[_col[2]] = _data
            elif _col[1] == ColType.Number.value:
                _data = float_int(self.item(row_, _idx).text())
                _data_dict[_col[2]] = _data
            elif _col[1] == ColType.Other.value:
                if _col[0] == TableCol.Type.value:
                    _data = self.__getattribute__(self.item(row_, _idx).text()).currentText()
                    _data_dict[_col[2]] = _data
        return _data_dict

    def _set_default(self, wgt_name_):
        _type = None
        for _row in range(self.rowCount()):
            for _idx, _col in enumerate(table_col):
                if _col[0] == TableCol.Type.value and self.item(_row, _idx).text() == wgt_name_:
                    _type = self.__getattribute__(self.item(_row, _idx).text()).currentText()
                    break
            if _type:
                for _idx, _col in enumerate(table_col):
                    if _col[1] in [ColType.String.value, ColType.Number.value]:
                        self.item(_row, _idx).setText(str(default_param[_type][_col[2]]))
                return
        raise ValueError("missing default value")

    def _price(self, row_):
        _raw_data = self._collect_row(row_)
        _inst = Instrument.get_inst(_raw_data)
        _mkt = deepcopy(self._parent.env_data)
        _engine = _mkt.pop(EnvParam.PricingEngine.value)
        _price = _inst.evaluate(_mkt, _engine)
        for _idx, _col in enumerate(table_col):
            if _col[0] == TableCol.Cost.value:
                self.item(row_, _idx).setText(str(round(_price, 2)))