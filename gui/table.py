# coding=utf-8
"""instrument table template"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView, QMessageBox, QTableWidgetItem
from copy import deepcopy
from enum import Enum
from gui.custom import CustomComboBox, CustomTableWidget
from gui.plot import PlotParam
from instrument import InstType, InstParam, Instrument, option_type
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
    Show = 'Show'


class ColType(Enum):
    """column type"""
    String = 0
    Number = 1
    Other = 2


table_col = [
    (TableCol.Type.value, ColType.Other.value, "Type", InstParam.InstType.value, 80),
    (TableCol.Strike.value, ColType.Number.value, "Strike", InstParam.OptionStrike.value, 50),
    (TableCol.Unit.value, ColType.Number.value, "Unit", InstParam.InstUnit.value, 50),
    (TableCol.Cost.value, ColType.Number.value, "Cost", InstParam.InstCost.value, 50),
    (TableCol.Show.value, ColType.Other.value, "", PlotParam.Show.value, 30),
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
        self.setHorizontalHeaderLabels([_col[2] for _col in table_col])
        for _idx, _col in enumerate(table_col):
            self.setColumnWidth(_idx, _col[4])
        self._col_width = sum([_col[4] for _col in table_col])
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.rightClicked.connect(self._price)

    def col_width(self):
        """return width sum of all columns"""
        return self._col_width

    def add_row(self, data_=None):
        """add a new instrument with given or default data"""
        self.setRowCount(self.rowCount() + 1)
        _id = self._inst_id()
        _type = data_.get(InstParam.InstType.value, default_type) if data_ else default_type

        for _idx, _col in enumerate(table_col):
            if _col[1] in [ColType.String.value, ColType.Number.value]:
                _default = default_param[_type].get(_col[3], '-')
                _content = data_.get(_col[3], _default) if data_ else _default
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
                    _wgt._wgt.setFixedWidth(_col[4])
                    self.__setattr__(_wgt_name, _wgt._wgt)
                    _wgt._wgt.changed.connect(self._set_default)
                    _wgt.setTextAlignment(Qt.AlignCenter)
                    self.setItem(self.rowCount() - 1, _idx, _wgt)
                    self.setCellWidget(self.rowCount() - 1, _idx, _wgt._wgt)
                elif _col[0] == TableCol.Show.value:
                    _wgt = QTableWidgetItem()
                    _wgt.setTextAlignment(Qt.AlignCenter)
                    _wgt.setCheckState(Qt.Unchecked)
                    self.setItem(self.rowCount() - 1, _idx, _wgt)
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
                self.item(self.rowCount() - 1, _idx).setText(str(_raw_data[_col[3]]))

            elif _col[1] == ColType.Other.value:
                if _col[0] == TableCol.Type.value:
                    self.__getattribute__(
                        self.item(self.rowCount() - 1, _idx).text()).setCurrentText(_raw_data[_col[3]])
                elif _col[0] == TableCol.Show.value:
                    self.item(self.rowCount() - 1, _idx).setCheckState(
                        Qt.Checked if _raw_data[_col[3]] else Qt.Unchecked)

    def delete_row(self):
        """delete an instrument"""
        if self.rowCount() == 1:
            QMessageBox.information(self, "Warning", "Only one option left, cannot be deleted.")
        else:
            _row = self.currentRow()
            self.removeRow(_row)

    def collect(self):
        """collect all instruments data"""
        return [self._collect_row_full(_row) for _row in range(self.rowCount())]

    def _collect_row_full(self, row_):
        _data_dict = self._collect_row(row_)
        _type = _data_dict.get(InstParam.InstType.value)
        if _type in option_type:
            _data_dict[InstParam.OptionMaturity.value] = self._parent.env_data[EnvParam.PortMaturity.value]
        return _data_dict

    def _collect_row(self, row_):
        _data_dict = dict()
        for _idx, _col in enumerate(table_col):
            if _col[1] == ColType.String.value:
                _data = self.item(row_, _idx).text()
                _data_dict[_col[3]] = _data
            elif _col[1] == ColType.Number.value:
                _data = float_int(self.item(row_, _idx).text())
                _data_dict[_col[3]] = _data
            elif _col[1] == ColType.Other.value:
                if _col[0] == TableCol.Type.value:
                    _data = self.__getattribute__(self.item(row_, _idx).text()).currentText()
                    _data_dict[_col[3]] = _data
                elif _col[0] == TableCol.Show.value:
                    _data = self.item(row_, _idx).checkState() == Qt.Checked
                    _data_dict[_col[3]] = _data
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
                        _default = default_param[_type].get(_col[3], '-')
                        self.item(_row, _idx).setText(str(_default))
                    elif _col[1] == ColType.Other.value:
                        if _col[0] == TableCol.Show.value:
                            _default = default_param[_type].get(_col[3], False)
                            self.item(_row, _idx).setCheckState(Qt.Checked if _default else Qt.Unchecked)
                return
        raise ValueError("missing default value of {}".format(wgt_name_))

    def _price(self, row_):
        if row_ == -1:
            return
        # prepare instrument data
        _raw_data = self._collect_row_full(row_)
        # prepare pricing environment
        _mkt = deepcopy(self._parent.env_data)
        _engine = _mkt.pop(EnvParam.PricingEngine.value)
        _rounding = _mkt.pop(EnvParam.CostRounding.value)
        # do pricing
        _inst = Instrument.get_inst(_raw_data)
        _price = _inst.evaluate(_mkt, _engine)
        for _idx, _col in enumerate(table_col):
            if _col[0] == TableCol.Cost.value:
                self.item(row_, _idx).setText(str(round(_price, _rounding)))

    def _inst_id(self):
        self._seq += 1
        return "Inst-{}".format(self._seq)
