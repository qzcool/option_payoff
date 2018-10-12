# coding=utf-8
"""
Vanilla Portfolio Payoff Curve Generator
Version 1.1.0 - alpha 1.1
Copyright: Tongyan Xu, 2018

This is a simple tool to estimate the payoff curve of vanilla portfolio.
"""

import sys
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView, QApplication, QComboBox, QFileDialog, QHBoxLayout, QMainWindow, QMenu
from PyQt5.QtWidgets import QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from json import dumps, loads
from plot import PayoffCurve
from option import Instrument, InstrumentType, OptionPortfolio, TransactionDirection
from gui.table import InstTable

default_param = [None for _type in InstrumentType]
default_param[InstrumentType.CALL.value] = dict(strike='100', price='0', unit='1')
default_param[InstrumentType.PUT.value] = dict(strike='100', price='0', unit='1')
default_param[InstrumentType.STOCK.value] = dict(strike='--', price='100', unit='1')

__help__ = ''''''


class ApplicationWindow(QMainWindow):
    """
    application main window
    an option editor on the left
    a payoff curve viewer on the right
    """
    def __init__(self):
        QMainWindow.__init__(self)
        # set basic parameters
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("Option Portfolio Payoff Curve")
        self.setGeometry(100, 100, 865, 450)
        # initialize basic widgets
        self._main = QWidget(self)
        self._plot = QWidget(self._main)
        self._table = QWidget(self._main)
        # initialize data storage
        self._data = []
        self._seq = 0
        self._last_path = '.'
        # setup and show
        self.set_ui()
        self.setCentralWidget(self._main)
        self.show()

    def set_ui(self):
        """setup menu, option editor, and payoff curve viewer"""
        self._set_menu()
        self._plot = PayoffCurve(dict(x=np.array([]), y=np.array([])), self._main)
        self._set_table()

        _main_layout = QHBoxLayout(self._main)
        _vbox = QVBoxLayout()
        _vbox.addWidget(self._table)
        self._add_button_group(_vbox)
        _main_layout.addLayout(_vbox)
        _main_layout.addWidget(self._plot)
        self._main.setFocus()

    def _load(self):
        _file_path, _file_type = QFileDialog.getOpenFileName(
            self, "Load Portfolio", self._last_path, "JSON Files (*.json)")
        if not _file_path:
            return

        with open(_file_path) as f:
            _raw_data = loads(f.read())
        self._last_path = _file_path

        if _raw_data:
            try:
                while self._table.rowCount():
                    self._table.removeRow(0)

                for _row in range(len(_raw_data)):
                    self._add_row()
                    self.__getattribute__(self._table.item(_row, 0).text()).setCurrentIndex(_raw_data[_row][0])
                    self.__getattribute__(self._table.item(_row, 1).text()).setCurrentIndex(_raw_data[_row][1])
                    self._table.item(_row, 2).setText(str(_raw_data[_row][2]) if _raw_data[_row][2] else '--')
                    self._table.item(_row, 3).setText(str(_raw_data[_row][3]))
                    self._table.item(_row, 4).setText(str(_raw_data[_row][4]))

            except Exception as e:
                QMessageBox.warning(self, "Load Portfolio", "Invalid data in {}\nError Message:{}".format(
                    _file_path, str(e)))

        else:
            QMessageBox.warning(self, "Load Portfolio", "No data found in {}".format(_file_path))

    def _save(self):
        _raw_data = self._collect_()

        if _raw_data:
            _file_path, _file_type = QFileDialog.getSaveFileName(
                self, "Save Portfolio", self._last_path, "JSON Files (*.json)")
            if not _file_path:
                return

            with open(_file_path, 'w') as f:
                f.write(dumps(_raw_data, indent=4))
            self._last_path = _file_path

    def _export(self):
        _file_path, _file_type = QFileDialog.getSaveFileName(
            self, "Save Portfolio", self._last_path, "PNG Files (*.png)")
        if not _file_path:
            return

        self._plot.save(_file_path)

    def _about(self):
        QMessageBox.about(self, "About", __doc__)

    def _help(self):
        QMessageBox.about(self, "Help", __help__)

    def _quit(self):
        self.close()

    def closeEvent(self, ce):
        """event when close button is clicked"""
        self._quit()

    def _set_menu(self):
        self._menu = self.menuBar()
        self._menu.setNativeMenuBar(False)

        _file = QMenu("&File", self)
        _file.addAction("&Load", self._load, Qt.CTRL + Qt.Key_L)
        _file.addAction("&Save", self._save, Qt.CTRL + Qt.Key_S)
        _file.addAction("&Export", self._export, Qt.CTRL + Qt.Key_E)
        _file.addAction("&Quit", self._quit, Qt.CTRL + Qt.Key_Q)
        self._menu.addMenu(_file)

        _config = QMenu("&Config", self)
        _config.addAction("&Market / Underlying", self._test)
        self._menu.addMenu(_config)

        _help = QMenu("&Help", self)
        _help.addAction("&Help", self._help, Qt.CTRL + Qt.Key_H)
        _help.addAction("&About", self._about, Qt.CTRL + Qt.Key_A)
        self._menu.addMenu(_help)

    def _add_button_group(self, layout_):
        _hbox = QHBoxLayout()
        _add_btn = QPushButton("Add")
        _add_btn.clicked.connect(self._add_row)
        _delete_btn = QPushButton("Delete")
        _delete_btn.clicked.connect(self._delete_row)
        _plot_btn = QPushButton("Plot")
        _plot_btn.clicked.connect(self._do_plot)
        _hbox.addWidget(_add_btn)
        _hbox.addWidget(_delete_btn)
        _hbox.addWidget(_plot_btn)
        layout_.addLayout(_hbox)

    def _set_table(self):
        self._table = InstTable()
        self._add_row()
        self._do_plot()

    def _add_row(self):
        if isinstance(self._table, QTableWidget):
            self._table.setRowCount(self._table.rowCount() + 1)

        _inst_id = self._inst_id()

        _wgt_name = "{}_type".format(_inst_id)
        _type = QTableWidgetItem(_wgt_name)
        from custom import CustomComboBox
        _type._wgt = CustomComboBox(wgt_name_=_wgt_name)
        for _inst_type in InstrumentType:
            _type._wgt.addItem(_inst_type.name)
        _type._wgt.setFixedWidth(80)
        self.__setattr__(_wgt_name, _type._wgt)
        _type._wgt.changed.connect(self._set_default)

        _wgt_name = "{}_direction".format(_inst_id)
        _direction = QTableWidgetItem(_wgt_name)
        _direction._wgt = QComboBox()
        for _trans_direction in TransactionDirection:
            _direction._wgt.addItem(_trans_direction.name)
        _direction._wgt.setFixedWidth(80)
        self.__setattr__(_wgt_name, _direction._wgt)

        _strike = QTableWidgetItem(default_param[0]['strike'])
        _strike.setTextAlignment(Qt.AlignCenter)

        _price = QTableWidgetItem(default_param[0]['price'])
        _price.setTextAlignment(Qt.AlignCenter)

        _unit = QTableWidgetItem(default_param[0]['unit'])
        _unit.setTextAlignment(Qt.AlignCenter)

        self._table.setItem(self._table.rowCount() - 1, 0, _type)
        self._table.setItem(self._table.rowCount() - 1, 1, _direction)
        self._table.setItem(self._table.rowCount() - 1, 2, _strike)
        self._table.setItem(self._table.rowCount() - 1, 3, _price)
        self._table.setItem(self._table.rowCount() - 1, 4, _unit)
        self._table.setCellWidget(self._table.rowCount() - 1, 0, _type._wgt)
        self._table.setCellWidget(self._table.rowCount() - 1, 1, _direction._wgt)

    def _delete_row(self):
        if self._table.rowCount() == 1:
            QMessageBox.information(self, "Warning", "Only one option left, cannot be deleted.")
        else:
            _row = self._table.currentRow()
            _type = self._table.item(_row, 0).text()
            self.__delattr__(_type)
            _direction = self._table.item(_row, 1).text()
            self.__delattr__(_direction)
            self._table.removeRow(_row)

    def _collect_(self):
        _raw_data = []
        for idx in range(self._table.rowCount()):
            try:
                _type = self.__getattribute__(self._table.item(idx, 0).text()).currentIndex()
                _direction = self.__getattribute__(self._table.item(idx, 1).text()).currentIndex()
                _strike = self._format(self._table.item(idx, 2).text()) if _type != InstrumentType.STOCK.value else None
                _price = self._format(self._table.item(idx, 3).text())
                _unit = self._format(self._table.item(idx, 4).text())

            except ValueError as e:
                QMessageBox.warning(self, "Collect Input",
                                    "Invalid input for instrument parameters\nError message: {}".format(str(e)))
                return None

            _raw_data.append((_type, _direction, _strike, _price, _unit))
        return _raw_data

    def _do_plot(self):
        _raw_data = self._collect_()
        if _raw_data:
            _option = [Instrument.get_inst(InstrumentType(_type), direction_=TransactionDirection(_direction),
                                           strike_=_strike, price_=_price, unit_=_unit)
                       for _type, _direction, _strike, _price, _unit in _raw_data]
            _portfolio = OptionPortfolio(_option)
            _x, _y = _portfolio.payoff_curve()
            self._plot.update_figure(dict(x=_x, y=_y))

    def _inst_id(self):
        self._seq += 1
        return "Inst-{}".format(self._seq)

    def _set_default(self, wgt_name_):
        for _row in range(self._table.rowCount()):
            if self._table.item(_row, 0).text() == wgt_name_:
                _type_value = self.__getattribute__(self._table.item(_row, 0).text()).currentIndex()
                self._table.item(_row, 2).setText(default_param[_type_value]['strike'])
                self._table.item(_row, 3).setText(default_param[_type_value]['price'])
                self._table.item(_row, 4).setText(default_param[_type_value]['unit'])

    @staticmethod
    def _format(string_):
        _number = float(string_)
        return _number if _number % 1 else int(_number)

    def _test(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = ApplicationWindow()
    sys.exit(app.exec_())
