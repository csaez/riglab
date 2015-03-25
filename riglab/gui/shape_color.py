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

import os
import sys

from wishlib.qt import QtGui, loadUi, set_style
from wishlib.utils import JSONDict
from rigicon import library


class ShapeColor(QtGui.QDialog):

    def __init__(self, parent=None):
        super(ShapeColor, self).__init__(parent)
        self.init_prefs()
        self.init_ui()

    def init_prefs(self):
        defaults = {"fkIcon": None,
                    "ikIcon": None,
                    "upIcon": None,
                    "C": [(0, 0, 0), (0, 0, 0)],
                    "L": [(0, 0, 0), (0, 0, 0)],
                    "R": [(0, 0, 0), (0, 0, 0)],
                    }
        self.prefs = JSONDict(
            os.path.join(os.path.expanduser("~"), "riglab", "shape_color.json"))
        for k, v in defaults.iteritems():
            if not self.prefs.get(k):
                self.prefs[k] = v

    def init_ui(self):
        ui_dir = os.path.join(os.path.dirname(__file__), "ui")
        self.ui = loadUi(os.path.join(ui_dir, "shape_color.ui"), self)
        # icons
        icons = [x.get("Name") for x in library.get_items()]
        for widget in (self.ui.fkIcon, self.ui.ikIcon, self.ui.upIcon):
            widget_name = str(widget.objectName())
            # set default values
            widget.addItems(icons)
            icon = self.prefs.get(widget_name)
            if icon:
                widget.setCurrentIndex(icons.index(icon))
            # signal
            widget.currentIndexChanged.connect(
                lambda x, w=widget: self.prefs.update({str(w.objectName()): str(w.currentText())}))
        # colors
        for w in (self.ui.L0, self.ui.L1, self.ui.C0, self.ui.C1, self.ui.R0, self.ui.R1):
            # set default values
            widget_name = str(w.objectName())
            color = self.prefs.get(widget_name[0])[int(widget_name[1])]
            style = "background-color: rgb({0}, {1}, {2});".format(*color)
            w.setStyleSheet(style)
            # signal
            w.clicked.connect(lambda x, widget=w: self.color_clicked(widget))

    # SLOTS
    def color_clicked(self, widget):
        print widget
        # get color from stylesheet
        style = str(widget.styleSheet())
        color = list(eval(style.split("rgb")[-1][:-1]))
        # launch color picker
        color_dialog = QtGui.QColorDialog(self)
        color_dialog.setCurrentColor(QtGui.QColor(*color))
        color_dialog.exec_()
        color = list(color_dialog.currentColor().getRgb())[:-1]
        # set color via stylesheet
        style = "background-color: rgb({0}, {1}, {2});".format(*color)
        widget.setStyleSheet(style)
        # update prefs
        widget_name = str(widget.objectName())
        data = self.prefs[widget_name[0]]
        data[int(widget_name[1])] = color
        self.prefs[widget_name[0]] = data

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    win = ShapeColor()
    set_style(win, True)
    win.show()
    app.exec_()
