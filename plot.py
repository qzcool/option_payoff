# coding=utf-8
"""plotting template"""

import numpy as np
from PyQt5.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MyMplCanvas(FigureCanvas):
    """DIY figure canvas"""
    def __init__(self, data_=None, parent_=None, width_=5, height_=4, dpi_=100):
        _fig = Figure(figsize=(width_, height_), dpi=dpi_)
        self._axes = _fig.add_subplot(111)
        self._plot_figure(data_)

        FigureCanvas.__init__(self, _fig)
        self.setParent(parent_)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def _plot_figure(self, data_):
        """plot figure using given data"""
        raise NotImplementedError("this method needs to be defined by subclass")


class PayoffCurve(MyMplCanvas):
    """figure canvas for plotting payoff curve"""

    def _plot_figure(self, data_):
        """
        plot payoff curve using given data
        :param data_: a dict consists with x (numpy array) and y (numpy array) in same dimension
        """
        _x = data_.get('x', np.array([]))
        _y = data_.get('y', np.array([]))
        if _x.size and _y.size:
            self._axes.plot(np.linspace(100, 100, _y.size), _y, color="grey", linewidth=1.5)
            self._axes.hold(True)
            if _y.min() <= 0 <= _y.max():
                self._axes.plot(_x, np.zeros(_x.size), color="grey", linewidth=1.5)
            self._axes.plot(_x, _y, 'r')
        self._axes.hold(False)
        self._set_axis()

    def update_figure(self, data_):
        """
        update payoff curve using new data
        :param data_: a dict consists with x (numpy array) and y (numpy array) in same dimension
        """
        self._plot_figure(data_)
        self.draw()
        
    def save(self, file_path_):
        """
        save figure to file using given path
        :param file_path_: a str indicating path to save figure file
        """
        self.print_png(file_path_)

    def _set_axis(self):
        self._axes.set_xlabel("Spot")
        self._axes.set_ylabel("Payoff")
        self._axes.set_title("Option Portfolio Payoff Curve")
        self._axes.grid(axis='x', linewidth=0.75, linestyle='-', color='0.75')
        self._axes.grid(axis='y', linewidth=0.75, linestyle='-', color='0.75')
