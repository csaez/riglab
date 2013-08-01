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
        self.save = True
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
        self.save = False  # disable save on rules and tokens update
        k = str(self.ui.items_listWidget.currentItem().text())
        # RULES
        if self.ui.rules_radioButton.isChecked():
            rule = self.nm.rules.get(k)
            self.ui.expr_lineEdit.setText(rule)
            self.save = True  # enable save on rules and tokens update
            return
        # TOKENS
        token = self.nm.tokens.get(k)
        classname = token.__class__.__name__
        # set visibility
        visibility = {"StringToken": (False, False, True, False, False),
                      "NumberToken": (False, True, False, True, False),
                      "DictToken": (True, False, False, False, True)}
        widgets = (self.ui.values_tableWidget,
                   self.ui.padding_frame,
                   self.ui.default_lineEdit,
                   self.ui.default_spinBox,
                   self.ui.default_comboBox)
        values = visibility.get(classname)
        if values:
            for widget, value in zip(widgets, values):
                widget.setVisible(value)
        # set values
        self.ui.default_groupBox.setChecked(token.default is not None)
        if classname == "StringToken":
            if token.default:
                self.ui.default_lineEdit.setText(token.default)
        elif classname == "NumberToken":
            self.ui.padding_spinBox.setValue(token.padding)
            if token.default:
                self.ui.default_spinBox.setValue(int(token.default))
        elif classname == "DictToken":
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
        self.save = True  # enable save on rules and tokens update

    def filter_changed(self, filter_text):
        self.list_clicked()

    def add_clicked(self):
        name = str(self.ui.filter_lineEdit.text())
        if len(name) and not self.ui.items_listWidget.count():
            if self.ui.rules_radioButton.isChecked():
                self.add_rule(name)
            else:
                self.add_token(name)

    def remove_clicked(self):
        if self.ui.items_listWidget.currentRow() != -1:
            name = str(self.ui.items_listWidget.currentItem().text())
            if self.ui.rules_radioButton.isChecked():
                del self.nm.rules[name]
            else:
                self.nm.tokens[name].destroy()  # remove json file
                del self.nm.tokens[name]
            self.list_clicked()

    def rule_updated(self, *args):
        # skip auto update
        if not self.save:
            return
        # validate
        cond = (self.ui.rules_radioButton.isChecked(),
                self.ui.items_listWidget.currentRow() != -1)
        if not all(cond):
            return
        # save expr
        name = str(self.ui.items_listWidget.currentItem().text())
        self.nm.rules[name] = str(self.ui.expr_lineEdit.text())

    def token_updated(self, *args):
        # skip auto updates
        if not self.save:
            return
        # validate
        cond = (self.ui.tokens_radioButton.isChecked(),
                self.ui.items_listWidget.currentRow() != -1)
        if not all(cond):
            return
        # get token
        name = str(self.ui.items_listWidget.currentItem().text())
        token = self.nm.tokens[name]
        classname = token.__class__.__name__
        # values
        if classname == "DictToken":
            for i in range(self.ui.values_tableWidget.rowCount()):
                k = self.ui.values_tableWidget.item(i, 0)
                v = self.ui.values_tableWidget.item(i, 1)
                if k and v:
                    token.values[str(k.text())] = str(v.text())
                    print token.values
        # defaults
        values = {"StringToken": (self.ui.default_groupBox.isChecked(),
                                  str(self.ui.default_lineEdit.text())),
                  "NumberToken": (self.ui.default_groupBox.isChecked(),
                                  self.ui.default_spinBox.value()),
                  "DictToken": (self.ui.default_groupBox.isChecked(),
                                str(self.ui.default_comboBox.currentText()))}
        self.ui.default_groupBox.setChecked(values.get(classname)[0])
        if values.get(classname)[0]:
            token.default = values.get(classname)[1]
        else:
            token.default = None
        # padding
        if hasattr(token, "padding"):
            token.padding = self.ui.padding_spinBox.value()
        # save changes
        token.save()

    def add_rule(self, name):
        self.nm.rules[name] = ""
        self.list_clicked()
        self.ui.items_listWidget.setCurrentRow(0)

    def add_token(self, name):
        menu = QtGui.QMenu(self)
        for classname in self.TOKEN_CLASSES:
            menu.addAction(classname)
        pos = QtGui.QCursor.pos()
        menu.move(pos.x(), pos.y())
        action = menu.exec_()
        if not action:
            return
        classname = str(action.text())
        self.nm.new_token(str(self.ui.filter_lineEdit.text()), classname)
        self.list_clicked()
        self.ui.items_listWidget.setCurrentRow(0)


def main():
    app = QtGui.QApplication(sys.argv)
    Editor().show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
