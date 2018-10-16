# coding=utf-8
"""customized widgets"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QCheckBox, QComboBox, QRadioButton, QSizePolicy, QTableWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class CustomCheckBox(QCheckBox):
    """customized check box to return widget name and value when current check state is changed"""
    changed = pyqtSignal(str, bool)

    def __init__(self, wgt_name_='CustomCheckBox', *args, **kwargs):
        super(CustomCheckBox, self).__init__(*args, **kwargs)
        self._wgt_name = wgt_name_
        self.stateChanged.connect(self._event)

    def name(self):
        """return widget name"""
        return self._wgt_name

    def _event(self):
        self.changed.emit(self._wgt_name, self.checkState())


class CustomComboBox(QComboBox):
    """customized combo box to return widget name when current index is changed"""
    changed = pyqtSignal(str)

    def __init__(self, wgt_name_='CustomComboBox', *args, **kwargs):
        super(CustomComboBox, self).__init__(*args, **kwargs)
        self._wgt_name = wgt_name_
        self.currentIndexChanged.connect(self._event)

    def name(self):
        """return widget name"""
        return self._wgt_name

    def _event(self):
        self.changed.emit(self._wgt_name)


class CustomRadioButton(QRadioButton):
    """customized radio button to return widget name when check state is changed"""
    changed = pyqtSignal(str)

    def __init__(self, wgt_name_='CustomRadioButton', *args, **kwargs):
        super(CustomRadioButton, self).__init__(*args, **kwargs)
        self._wgt_name = wgt_name_
        self.toggled.connect(self._event)

    def name(self):
        """return widget name"""
        return self._wgt_name

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
    """customized table widget to enable right click events"""
    rightClicked = pyqtSignal(int)

    def mousePressEvent(self, e):
        """..."""
        super(CustomTableWidget, self).mousePressEvent(e)
        if e.buttons() == Qt.RightButton:
            self.rightClicked.emit(self.currentRow())
