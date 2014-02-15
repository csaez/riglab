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
from collections import namedtuple

from wishlib.qt import QtGui, loadUi
from naming import Manager as nm


class Rename(QtGui.QDialog):
    side_data = nm().tokens["side"].values
    data_type = namedtuple("name_data", ["name", "side"])

    def __init__(self, parent=None):
        super(Rename, self).__init__(parent)
        ui_dir = os.path.join(os.path.dirname(__file__), "ui")
        self.ui = loadUi(os.path.join(ui_dir, "rename.ui"), self)
        self.setWindowTitle("Rename item")

    @classmethod
    def get_data(cls, parent=None, name=None, side="center"):
        d = cls(parent)
        if name:
            d.ui.name.setText(name)
        # add sides from naming convention
        d.ui.side.clear()
        d.ui.side.addItems([x.capitalize() for x in cls.side_data.keys()])
        # set default side
        side = side.lower()
        for i, (k, v) in enumerate(cls.side_data.iteritems()):
            if side == k.lower() or side == v.lower():
                d.ui.side.setCurrentIndex(i)
        ok = d.exec_()
        result = (str(d.ui.name.text()),
                  d.side_data.get(str(d.ui.side.currentText()).lower()))
        return ok, cls.data_type._make(result)
