# coding=utf-8
"""customized widgets"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QComboBox, QSizePolicy, QTableWidgetItem, QTableWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class CustomComboBox(QComboBox):
    """customized combo box to return widget name when current index is changed"""
    changed = pyqtSignal(str)

    def __init__(self, parent_=None, wgt_name_='CustomComboBox'):
        super(CustomComboBox, self).__init__(parent_)
        self._wgt_name = wgt_name_
        self.currentIndexChanged.connect(self._event)

    def _event(self):
        self.changed.emit(self._wgt_name)


class CustomMplCanvas(FigureCanvas):
    """DIY figure canvas"""
    def __init__(self, data_=None, parent_=None, width_=5, height_=4, dpi_=100):
        self._fig = Figure(figsize=(width_, height_), dpi=dpi_)
        self._axes = self._fig.add_subplot(111)
        self._plot_figure(data_)

        FigureCanvas.__init__(self, self._fig)
        self.setParent(parent_)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def _plot_figure(self, data_):
        """plot figure using given data"""
        raise NotImplementedError("this method needs to be defined by subclass")


class CustomTableWidget(QTableWidget):
    """customized combo box to return widget name when current index is changed"""
    rightClicked = pyqtSignal(int)

    def mousePressEvent(self, e):
        """..."""
        super(CustomTableWidget, self).mousePressEvent(e)
        if e.buttons() == Qt.RightButton:
            self.rightClicked.emit(self.currentRow())
