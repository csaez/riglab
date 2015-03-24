# This file is part of riglab.
# Copyright (C) 2014  Cesar Saez

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from difflib import SequenceMatcher

from wishlib.si import sisel
from wishlib.qt import QtGui, QtCore


class TableSwitcher(QtGui.QTableWidget):

    def dropEvent(self, dropEvent):
        item_src = self.selectedItems()[0]
        item_dest = self.itemAt(dropEvent.pos())
        src_row = item_src.row()
        src_col = item_src.column()
        dest_value = item_dest.text()
        super(TableSwitcher, self).dropEvent(dropEvent)
        self.setItem(src_row, src_col, QtGui.QTableWidgetItem(dest_value))


class Mapping(QtGui.QDialog):

    def __init__(self, *args, **kwds):
        super(Mapping, self).__init__(*args, **kwds)
        self.data = {}
        self.setup_ui()

    def setup_ui(self):
        self.resize(485, 410)
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.setMargin(6)
        self.verticalLayout = QtGui.QVBoxLayout()
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
        self.verticalLayout.addWidget(self.skeleton)
        self.icons = QtGui.QCheckBox(self)
        self.icons.setText("Transfer curves")
        self.icons.setChecked(True)
        self.verticalLayout.addWidget(self.icons)
        self.negate = QtGui.QCheckBox(self)
        self.negate.setText("Negate transforms (symmetry)")
        self.verticalLayout.addWidget(self.negate)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(
            QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.horizontalLayout.addWidget(self.buttonBox)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

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
        self.data["skeleton"] = self.skeleton_dict
        self.data["icons"] = self.icons.isChecked()
        self.data["negate"] = self.negate.isChecked()
        super(Mapping, self).accept()

    @classmethod
    def get(cls, parent, skeleton_dict):
        m = cls(parent)
        m.reload(skeleton_dict)
        if m.exec_():
            return m.data
