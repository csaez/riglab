import os
import sys

from wishlib.qt.QtGui import QDialog
from PyQt4 import QtGui, uic

from ..naming import get_rules, get_tokens


class Naming(QDialog):

    def __init__(self, parent=None):
        super(Naming, self).__init__(parent)
        self.initUI()

    def initUI(self):
        ui_dir = os.path.join(os.path.dirname(__file__), "ui")
        self.ui = uic.loadUi(os.path.join(ui_dir, "naming.ui"), self)
        self.ui.tokenProperties_frame.setHidden(True)

    def contents_changed(self, tab_index):
        value = bool(tab_index)
        self.ui.ruleProperties_frame.setHidden(value)
        self.ui.tokenProperties_frame.setHidden(not value)
        self.ui.rules_listWidget.clear()
        items = get_rules()
        if value:
            items = get_tokens()
        self.ui.rules_listWidget.addItems(items)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Naming().show()
    sys.exit(app.exec_())
