# coding=utf-8
"""
Vanilla Portfolio Ralated Curve Generator
Version 1.2.15
Copyright: Tongyan Xu, 2018

A simple tool to estimate the payoff / profit / pv / delta curve of vanilla portfolios.

Pricing is now available for vanilla options based on Black-Scholes or Monte-Carlo methods.
"""

from sys import argv as sys_argv, exit as sys_exit
from numpy import array
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QMainWindow, QMenu, QMessageBox, QPushButton
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from gui.help import HelpDialog
from gui.table import InstTable
from gui.plot import PayoffCurve, PlotParam
from gui.pricing_env import PricingEnv, parse_env
from instrument import Instrument
from instrument.default_param import env_default_param
from instrument.env_param import EngineMethod
from instrument.portfolio import CurveType, Portfolio
from json import dumps, loads


class ApplicationWindow(QMainWindow):
    """
    application main window
    an instrument editor on the left
    a curve viewer on the right
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
        self._env_box = None
        self._help_box = None
        # initialize data storage
        self.env_data = env_default_param
        self._last_path = '.'
        # setup and show
        self.setup_ui()
        self.setCentralWidget(self._main)
        self.setGeometry(QRect(100, 100, 556 + self._table.col_width(), 480))
        self.show()

    def setup_ui(self):
        """setup menu, option editor, and payoff curve viewer"""
        self._set_menu()
        self._plot = PayoffCurve(dict(x=array([]), y=array([]), type="Payoff"), self._main)
        self._set_table()

        _main_layout = QHBoxLayout(self._main)

        _vbox = QVBoxLayout()
        _vbox.addWidget(self._table)
        _vbox.addLayout(self._inst_btn_layout())
        _main_layout.addLayout(_vbox)

        _vbox = QVBoxLayout()
        _vbox.addWidget(self._plot)
        _vbox.addLayout(self._plot_btn_layout())
        _main_layout.addLayout(_vbox)

        self._main.setFocus()

    def _load(self):
        _file_path, _file_type = QFileDialog.getOpenFileName(
            self, "Load Portfolio", self._last_path, "JSON Files (*.json)")
        if not _file_path:
            return

        with open(_file_path) as f:
            _input_data = loads(f.read())
        self._last_path = _file_path

        _raw_data = _input_data.get('data')
        _env = _input_data.get('env')

        if _raw_data and _env:
            self.env_data = _env
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
        _output = dict(data=_raw_data, env=self.env_data)

        if _raw_data:
            _file_path, _file_type = QFileDialog.getSaveFileName(
                self, "Save Portfolio", self._last_path, "JSON Files (*.json)")
            if not _file_path:
                return

            with open(_file_path, 'w') as f:
                f.write(dumps(_output, indent=4))
            self._last_path = _file_path

    def _export(self):
        _file_path, _file_type = QFileDialog.getSaveFileName(
            self, "Save Portfolio", self._last_path, "PNG Files (*.png)")
        if not _file_path:
            return

        self._plot.save(_file_path)

    def _pricing_env(self):
        self._env_box = PricingEnv(self)

    def _about(self):
        QMessageBox.about(self, "About", __doc__)

    def _help(self):
        self._help_box = HelpDialog(self)

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

        _plot_btn = QPushButton("Payoff Curve")
        _plot_btn.clicked.connect(self._plot_payoff)
        _hbox.addWidget(_plot_btn)

        _plot_btn = QPushButton("Profit Curve")
        _plot_btn.clicked.connect(self._plot_profit)
        _hbox.addWidget(_plot_btn)

        _plot_btn = QPushButton("PV Curve")
        _plot_btn.clicked.connect(self._plot_pv)
        _hbox.addWidget(_plot_btn)

        _plot_btn = QPushButton("Delta Curve")
        _plot_btn.clicked.connect(self._plot_delta)
        _hbox.addWidget(_plot_btn)

        return _hbox

    def _set_table(self):
        self._table = InstTable(self)
        self._add()
        self._plot_payoff()

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

    def _prepare_data(self):
        _raw_data = self._table.collect()
        _inst = [Instrument.get_inst(_data) for _data in _raw_data] if _raw_data else []
        _inst_show = [Instrument.get_inst(_data)
                      for _data in filter(lambda x: x[PlotParam.Show.value], _raw_data)] if _raw_data else []
        _portfolio = Portfolio(_inst)
        _mkt, _engine, _rounding = parse_env(self.env_data)
        _portfolio.set_mkt(_mkt)
        _portfolio.set_engine(_engine)
        _portfolio.set_show(_inst_show)
        return _portfolio

    def _plot_payoff(self):
        self._plot_impl(CurveType.Payoff.value)

    def _plot_profit(self):
        self._plot_impl(CurveType.Profit.value)

    def _plot_pv(self):
        self._plot_impl(CurveType.PV.value)

    def _plot_delta(self):
        self._plot_impl(CurveType.Delta.value)

    def _plot_impl(self, type_):
        _portfolio = self._prepare_data()
        if type_ == CurveType.PV.value and _portfolio.engine['engine'] == EngineMethod.MC.value:
            if QMessageBox.question(
                    self, "Evaluation Cure",
                    "Using Monte-Carlo to generate Evaluation Curve might be extremely time consuming. "
                    "Are you sure to continue?") == QMessageBox.No:
                return
        _x, _y = _portfolio.gen_curve(type_, full_=True)
        _x_ref = 0 if type_ == CurveType.Profit.value else 100 if _portfolio.has_stock() else 0
        self._plot.update_figure(dict(x=_x, y=_y, type=type_, x_ref=_x_ref, y_ref=_portfolio.isp()))

    def _test(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys_argv)
    main = ApplicationWindow()
    sys_exit(app.exec_())
