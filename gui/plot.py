# coding=utf-8
"""plotting template"""

import numpy as np
from gui.custom import CustomMplCanvas


class PayoffCurve(CustomMplCanvas):
    """figure canvas for plotting payoff curve"""

    def _plot_figure(self, data_):
        """
        plot payoff curve using given data
        :param data_: a dict consists with x (numpy array) and y (numpy array) in same dimension
        """
        _x = data_.get('x', np.array([]))
        _y = data_.get('y', np.array([]))
        _type = data_.get('type')
        if not _type:
            raise ValueError("plot type is required")

        if _x.size and _y.size:
            self._axes.clear()
            self._axes.plot(np.linspace(100, 100, _y.size), _y, color="grey", linewidth=1.5)
            if _y.min() <= 0 <= _y.max():
                self._axes.plot(_x, np.zeros(_x.size), color="grey", linewidth=1.5)
            if _type == "Payoff":
                self._prepare_payoff(_x, _y)
            self._axes.plot(_x, _y, 'r')

        self._set_axis(_type)

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

    def _prepare_payoff(self, x_, y_):
        if y_.min() <= 100 <= y_.max():
            self._axes.plot(x_, np.zeros(x_.size) + 100, color="grey", linewidth=1.5)

    def _set_axis(self, type_):
        self._axes.set_xlabel("Spot (% of ISP)")
        _time = "T0" if type_ == "Return" else "T"
        self._axes.set_ylabel(type_)
        self._axes.set_title("Option Portfolio {} Curve on {}".format(type_, _time))
        self._axes.grid(axis='x', linewidth=0.75, linestyle='-', color='0.75')
        self._axes.grid(axis='y', linewidth=0.75, linestyle='-', color='0.75')
