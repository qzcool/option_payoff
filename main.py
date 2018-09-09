# coding=utf-8
"""
Option Portfolio Payoff Curve Generator
Version 1.0.4
Copyright: Tongyan Xu, 2018

This is a simple tool to estimate the payoff curve of option portfolio.

Currently, only vanilla options could be taken into consideration.

Pricing is not available and option price need to be set manually.
"""

import sys
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView, QApplication, QComboBox, QHBoxLayout, QMainWindow, QMenu, QMessageBox
from PyQt5.QtWidgets import QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from plot import PayoffCurve
from option import Instrument, OptionPortfolio


class ApplicationWindow(QMainWindow):
    """
    application main window
    an option editor on the left
    a payoff curve viewer on the right
    """
    def __init__(self):
        QMainWindow.__init__(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("Option Portfolio Payoff Curve")
        self.setGeometry(100, 100, 865, 450)
        self._main = QWidget(self)
        self._plot = QWidget(self._main)
        self._table = QWidget(self._main)
        self._seq = 0
        self.set_ui()
        self.setCentralWidget(self._main)

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

    def run(self):
        """run main window"""
        self.show()

    def _about(self):
        QMessageBox.about(self, "About", __doc__)

    def _quit(self):
        self.close()

    def closeEvent(self, ce):
        """event when close button is clicked"""
        self._quit()

    def _set_menu(self):
        self._menu = self.menuBar()
        self._menu.setNativeMenuBar(False)

        _file = QMenu("&File", self)
        _file.addAction("&Quit", self._quit, Qt.CTRL + Qt.Key_Q)
        self._menu.addMenu(_file)

        _help = QMenu("&Help", self)
        _help.addAction("&About", self._about)
        self._menu.addMenu(_help)

    def _add_button_group(self, layout_):
        _hbox = QHBoxLayout()
        _add_btn = QPushButton("Add")
        _add_btn.clicked.connect(self._add_row)
        _delete_btn = QPushButton("Delete")
        _delete_btn.clicked.connect(self._delete_row)
        _plot_btn = QPushButton("Plot")
        _plot_btn.clicked.connect(self._collect_option)
        _hbox.addWidget(_add_btn)
        _hbox.addWidget(_delete_btn)
        _hbox.addWidget(_plot_btn)
        layout_.addLayout(_hbox)

    def _set_table(self):
        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels(["Type", "Direction", "Strike", "Price", "Unit"])
        self._table.setColumnWidth(0, 80)
        self._table.setColumnWidth(1, 80)
        self._table.setColumnWidth(2, 50)
        self._table.setColumnWidth(3, 50)
        self._table.setColumnWidth(4, 50)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._add_row()
        self._collect_option()

    def _add_row(self):
        if isinstance(self._table, QTableWidget):
            self._table.setRowCount(self._table.rowCount() + 1)

        _option_id = self._option_id()

        _wgt_name = "{}_type".format(_option_id)
        _type = QTableWidgetItem(_wgt_name)
        _type._wgt = QComboBox()
        _type._wgt.addItem("CALL")
        _type._wgt.addItem("PUT")
        # _type._wgt.addItem("STOCK")
        _type._wgt.setFixedWidth(80)
        self.__setattr__(_wgt_name, _type._wgt)

        _wgt_name = "{}_direction".format(_option_id)
        _direction = QTableWidgetItem(_wgt_name)
        _direction._wgt = QComboBox()
        _direction._wgt.addItem("LONG")
        _direction._wgt.addItem("SHORT")
        _direction._wgt.setFixedWidth(80)
        self.__setattr__(_wgt_name, _direction._wgt)

        _strike = QTableWidgetItem("100")
        _strike.setTextAlignment(Qt.AlignCenter)

        _price = QTableWidgetItem("0")
        _price.setTextAlignment(Qt.AlignCenter)

        _unit = QTableWidgetItem("1")
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

    def _collect_option(self):
        _option = []
        for idx in range(self._table.rowCount()):
            _type = self.__getattribute__(self._table.item(idx, 0).text()).currentText()
            _direction = self.__getattribute__(self._table.item(idx, 1).text()).currentText()
            _strike = float(self._table.item(idx, 2).text())
            _price = float(self._table.item(idx, 3).text())
            _unit = int(self._table.item(idx, 4).text())
            _option.append(
                Instrument.get_inst(_type, direction_=_direction, strike_=_strike, price_=_price, unit_=_unit))
        _portfolio = OptionPortfolio(_option)
        _x, _y = _portfolio.payoff_curve()
        self._plot.update_figure(dict(x=_x, y=_y))

    def _option_id(self):
        self._seq += 1
        return "Option-{}".format(self._seq)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = ApplicationWindow()
    main.run()
    sys.exit(app.exec_())
