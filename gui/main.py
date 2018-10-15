# coding=utf-8
"""
Vanilla Portfolio Payoff Curve Generator
Version 1.1.8
Copyright: Tongyan Xu, 2018

This is a simple tool to estimate the payoff curve of vanilla portfolio.

Pricing is now available for vanilla option based on Black-Scholes or Monte-Carlo.
"""

import sys
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QMainWindow, QMenu, QMessageBox, QPushButton
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from gui.table import InstTable
from gui.plot import PayoffCurve
from gui.pricing_env import PricingEnv
from instrument import Instrument
from instrument.default_param import env_default_param
from instrument.portfolio import Portfolio
from json import dumps, loads

__help__ = '''
Parameters' Instructions:
1. Strike - strike level of an OPTION
    * marked as % of underlying ISP
2. Maturity - maturity of an OPTION
    * marked as number of YEARS
3. Unit - unit of each instrument
    * could be a FLOAT number
    * could be NEGATIVE indicating SHORT position
4. Cost - unit cost level of an OPTION
    * marked as % of underlying ISP

Pricing Tips:
1. Right click an OPTION for auto pricing
    * right click on the target line
2. Edit pricing env in Menu - Config - Pricing Env

Pricing Parameters:
1. risk free rate (discrete, %, default 3)
    * will be shifted to continuous term
    * r_c = (ln(1 + r / 100) - 1) * 100
2. underlying volatility (%, default 5)
3. dividend yield ratio (discrete, %, default 0)
    * will be shifted to continuous term
    * div_c = (ln(1 + div / 100) - 1) * 100
4. cost rounding (default 2)
5. pricing engine (default Black-Scholes)
'''


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
        # initialize basic widgets
        self._main = QWidget(self)
        self._plot = QWidget(self._main)
        self._table = QWidget(self._main)
        # initialize data storage
        self.env_data = env_default_param
        self._last_path = '.'
        # setup and show
        self.setup_ui()
        self.setCentralWidget(self._main)
        self.setGeometry(100, 100, 556 + self._table.col_width(), 450)
        self.show()

    def setup_ui(self):
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

                for _row in _raw_data:
                    self._add(_row)

            except Exception as e:
                QMessageBox.warning(self, "Load Portfolio", "Invalid data in {}\nError Message:{}".format(
                    _file_path, str(e)))

        else:
            QMessageBox.warning(self, "Load Portfolio", "No data found in {}".format(_file_path))

    def _save(self):
        _raw_data = self._collect()

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

    def _pricing_env(self):
        self._pricing_env = PricingEnv(self)

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
        _config.addAction("&Pricing Env", self._pricing_env, Qt.CTRL + Qt.Key_P)
        self._menu.addMenu(_config)

        _help = QMenu("&Help", self)
        _help.addAction("&Help", self._help, Qt.CTRL + Qt.Key_H)
        _help.addAction("&About", self._about, Qt.CTRL + Qt.Key_A)
        self._menu.addMenu(_help)

    def _add_button_group(self, layout_):
        _vbox = QVBoxLayout()
        _vbox.addLayout(self._inst_btn_layout())
        _vbox.addLayout(self._plot_btn_layout())
        layout_.addLayout(_vbox)

    def _inst_btn_layout(self):
        _hbox = QHBoxLayout()

        _add_btn = QPushButton("Add")
        _add_btn.clicked.connect(self._add)
        _hbox.addWidget(_add_btn)

        _copy_btn = QPushButton("Copy")
        _copy_btn.clicked.connect(self._copy)
        _hbox.addWidget(_copy_btn)

        _delete_btn = QPushButton("Delete")
        _delete_btn.clicked.connect(self._delete)
        _hbox.addWidget(_delete_btn)

        return _hbox

    def _plot_btn_layout(self):
        _hbox = QHBoxLayout()

        _plot_btn = QPushButton("Plot")
        _plot_btn.clicked.connect(self._do_plot)
        _hbox.addWidget(_plot_btn)

        return _hbox

    def _set_table(self):
        self._table = InstTable(self)
        self._add()
        self._do_plot()

    def _add(self, data_=None):
        try:
            self._table.add_row(data_)
        except Exception as e:
            QMessageBox.warning(
                self, "Add Instrument", "An error occurred while adding new instrument: {}".format(str(e)))

    def _copy(self):
        self._table.copy_row()

    def _delete(self):
        self._table.delete_row()

    def _collect(self):
        return self._table.collect()

    def _do_plot(self):
        _raw_data = self._table.collect()
        if _raw_data:
            _inst = [Instrument.get_inst(_data) for _data in _raw_data]
            _portfolio = Portfolio(_inst)
            _x, _y = _portfolio.payoff_curve()
            self._plot.update_figure(dict(x=_x, y=_y))

    def _test(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = ApplicationWindow()
    sys.exit(app.exec_())
