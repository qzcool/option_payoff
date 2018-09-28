# coding=utf-8
"""customized widgets"""

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QComboBox


class CustomComboBox(QComboBox):
    """customized combo box to return widget name when current index is changed"""
    changed = pyqtSignal(str)

    def __init__(self, parent_=None, wgt_name_='CustomComboBox'):
        super(CustomComboBox, self).__init__(parent_)
        self._wgt_name = wgt_name_
        self.currentIndexChanged.connect(self._event)

    def _event(self):
        self.changed.emit(self._wgt_name)
