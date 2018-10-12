# coding=utf-8
"""..."""

from enum import Enum
from instrument import InstParam
from PyQt5.QtWidgets import QAbstractItemView, QTableWidget


class TableCol(Enum):
    """..."""
    Type = 'Type'
    Unit = 'Unit'
    Price = 'Price'
    Detail = 'Detail'


class ColType(Enum):
    """..."""
    Text = 0
    Button = 1
    ComboBox = 2


table_col = [
    (TableCol.Type.value, ColType.ComboBox, InstParam.InstType.value, 80),
    (TableCol.Unit.value, ColType.Text, InstParam.InstUnit.value, 50),
    (TableCol.Price.value, ColType.Text, InstParam.InstPrice.value, 50),
    (TableCol.Detail.value, ColType.Button, None, 50),
    ('?',1,1,50)
]


class InstTable(QTableWidget):
    """..."""
    def __init__(self, *args, **kwargs):
        super(InstTable, self).__init__(0, len(table_col), *args, **kwargs)
        self.setHorizontalHeaderLabels([_col[0] for _col in table_col])
        for _idx, _col in enumerate(table_col):
            self.setColumnWidth(_idx, _col[3])
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

    def add_row(self):
        """..."""
        pass
