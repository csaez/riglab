from difflib import SequenceMatcher

from PyQt4 import QtGui, QtCore
from wishlib.si import sisel
from wishlib.qt.QtGui import QDialog


class TableSwitcher(QtGui.QTableWidget):

    def dropEvent(self, dropEvent):
        item_src = self.selectedItems()[0]
        item_dest = self.itemAt(dropEvent.pos())
        src_row = item_src.row()
        src_col = item_src.column()
        dest_value = item_dest.text()
        super(TableSwitcher, self).dropEvent(dropEvent)
        self.setItem(src_row, src_col, QtGui.QTableWidgetItem(dest_value))


class Mapping(QDialog):

    def __init__(self, *args, **kwds):
        super(Mapping, self).__init__(*args, **kwds)
        self.setup_ui()

    def setup_ui(self):
        self.resize(485, 410)
        horizontalLayout = QtGui.QHBoxLayout(self)
        horizontalLayout.setMargin(6)
        self.skeleton = TableSwitcher(self)
        self.skeleton.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.skeleton.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.skeleton.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.skeleton.setCornerButtonEnabled(False)
        self.skeleton.setColumnCount(1)
        self.skeleton.setRowCount(0)
        item = QtGui.QTableWidgetItem("Skeleton")
        self.skeleton.setHorizontalHeaderItem(0, item)
        self.skeleton.horizontalHeader().setVisible(True)
        self.skeleton.horizontalHeader().setStretchLastSection(True)
        horizontalLayout.addWidget(self.skeleton)
        verticalLayout = QtGui.QVBoxLayout()
        buttonBox = QtGui.QDialogButtonBox(self)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            buttonBox.sizePolicy().hasHeightForWidth())
        buttonBox.setSizePolicy(sizePolicy)
        buttonBox.setOrientation(QtCore.Qt.Vertical)
        buttonBox.setStandardButtons(
            QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        verticalLayout.addWidget(buttonBox)
        spacerItem = QtGui.QSpacerItem(
            20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        verticalLayout.addItem(spacerItem)
        horizontalLayout.addLayout(verticalLayout)
        # connect signals
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def reload(self, skeleton_dict):
        ratio = lambda x, y: SequenceMatcher(None, x, y). ratio()
        self.labels = skeleton_dict.keys()
        target = [x.FullName for x in sisel]
        for i, n in enumerate(self.labels):
            # get closest by ratio
            closest = None
            if len(target):
                closest = sorted(target, key=lambda t: ratio(n, t))[-1]
                target.remove(closest)
            # gui stuff
            self.skeleton.insertRow(i)
            item = QtGui.QTableWidgetItem(closest or "")
            self.skeleton.setItem(0, i, item)
        self.skeleton.setVerticalHeaderLabels(self.labels)
        self.skeleton_dict = skeleton_dict

    def accept(self):
        keys = self.skeleton_dict.keys()
        for i, k in enumerate(keys):
            item = self.skeleton.item(0, i)
            self.skeleton_dict[k] = str(item.text())
        super(Mapping, self).accept()

    @classmethod
    def get(cls, parent, skeleton_dict):
        m = cls(parent)
        m.reload(skeleton_dict)
        if m.exec_():
            return m.skeleton_dict
