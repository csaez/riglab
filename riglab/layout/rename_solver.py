import os
import sys
from collections import namedtuple

from PyQt4 import QtGui, uic


class RenameSolver(QtGui.QDialog):

    def __init__(self, parent=None):
        super(RenameSolver, self).__init__(parent)
        ui_dir = os.path.join(os.path.dirname(__file__), "ui")
        self.ui = uic.loadUi(os.path.join(ui_dir, "rename_solver.ui"), self)

    def accept(self):
        super(RenameSolver, self).accept()

    @classmethod
    def get_data(cls, parent=None, name=None, side_items=None):
        d = cls(parent)
        if name:
            d.ui.name.setText(name)
        if side_items:
            d.ui.side.setItems(side_items)
        ok = d.exec_()
        result = (str(d.ui.name.text()), str(d.ui.side.currentText()))
        return ok, namedtuple("name_data", ["name", "side"])._make(result)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    print RenameSolver.get_data()
    sys.exit()
