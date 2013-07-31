import os
import sys

from wishlib.qt.QtGui import QMainWindow
from PyQt4 import QtGui, uic

from riglab.naming import Manager


class Editor(QMainWindow):
    TOKEN_CLASSES = ("StringToken", "NumberToken", "DictToken")

    def __init__(self, parent=None):
        super(Editor, self).__init__(parent)
        self.nm = Manager()  # naming manager
        self.initUI()

    def initUI(self):
        ui_dir = os.path.join(os.path.dirname(__file__), "ui")
        self.ui = uic.loadUi(os.path.join(ui_dir, "namingEditor.ui"), self)
        # update gui
        self.list_clicked()

    def list_clicked(self):
        vis = self.ui.rules_radioButton.isChecked()
        # set visibility
        self.ui.rules_frame.setVisible(vis)
        self.ui.tokens_frame.setVisible(not vis)
        # list items
        items = self.nm.rules.keys()
        if not vis:
            items = self.nm.tokens.keys()
        filter_text = str(self.ui.filter_lineEdit.text())
        items = [x for x in items if filter_text in x]
        self.ui.items_listWidget.clear()
        self.ui.items_listWidget.addItems(items)
        self.list_changed(-1)

    def list_changed(self, index):
        # enable properties
        enabled = self.ui.items_listWidget.currentRow() != -1
        self.ui.rules_frame.setEnabled(enabled)
        self.ui.tokens_frame.setEnabled(enabled)
        if not enabled:
            return
        k = str(self.ui.items_listWidget.currentItem().text())
        # RULES
        if self.ui.rules_radioButton.isChecked():
            rule = self.nm.rules.get(k)
            self.ui.expr_lineEdit.setText(rule)
            return
        # TOKENS
        token = self.nm.tokens.get(k)
        token_classname = token.__class__.__name__
        # set visibility
        visibility = {"StringToken": (False, False, True, False, False),
                      "NumberToken": (False, True, False, True, False),
                      "DictToken": (True, False, False, False, True)}
        widgets = (self.ui.values_tableWidget,
                   self.ui.padding_frame,
                   self.ui.default_lineEdit,
                   self.ui.default_spinBox,
                   self.ui.default_comboBox)
        values = visibility.get(token_classname)
        if values:
            for widget, value in zip(widgets, values):
                widget.setVisible(value)
        # set values
        self.ui.default_groupBox.setChecked(token.default is not None)
        if token_classname == "StringToken":
            if token.default:
                self.ui.default_lineEdit.setText(token.default)
        elif token_classname == "NumberToken":
            self.ui.padding_spinBox.setValue(token.padding)
            if token.default:
                self.ui.default_spinBox.setValue(int(token.default))
        elif token_classname == "DictToken":
            for __ in range(self.ui.values_tableWidget.rowCount()):
                self.ui.values_tableWidget.removeRow(0)
            self.ui.default_comboBox.clear()
            index_default = -1
            for i, (k, v) in enumerate(token.values.iteritems()):
                self.ui.values_tableWidget.insertRow(i)
                self.ui.default_comboBox.addItem(k)
                if token.default == v:
                    index_default = i
                k, v = QtGui.QTableWidgetItem(k), QtGui.QTableWidgetItem(v)
                self.ui.values_tableWidget.setItem(i, 0, k)
                self.ui.values_tableWidget.setItem(i, 1, v)
            if index_default != -1:
                self.ui.default_comboBox.setCurrentIndex(index_default)

    def filter_changed(self, filter_text):
        self.list_clicked()

    def add_clicked(self):
        pass

    def remove_clicked(self):
        pass


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Editor().show()
    sys.exit(app.exec_())
