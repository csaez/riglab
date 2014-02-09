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

from PyQt4 import uic, QtGui
from naming import Manager as nm


class SpaceName(QtGui.QDialog):
    side_data = nm().tokens["side"].values
    data_type = namedtuple("space_data", ["name", "type"])

    def __init__(self, parent=None):
        super(SpaceName, self).__init__(parent)
        ui_dir = os.path.join(os.path.dirname(__file__), "ui")
        self.ui = uic.loadUi(os.path.join(ui_dir, "rename.ui"), self)
        self.setWindowTitle("Space Name")
        self.ui.space_type = self.ui.side
        self.ui.side_label.setText("Type")

    @classmethod
    def get_data(cls, parent=None, space_name=None, space_type="parent"):
        types = ("Parent", "Orient", "Reader")
        # validate
        if space_type.capitalize() not in types:
            return
        d = cls(parent)
        if space_name:
            d.ui.name.setText(space_name)
        # add space_types
        d.ui.space_type.clear()
        d.ui.space_type.addItems(types)
        d.ui.space_type.setCurrentIndex(
            types.index(space_type.capitalize()))
        ok = d.exec_()
        result = (str(d.ui.name.text()),
                  str(d.ui.space_type.currentText()).lower())
        return ok, cls.data_type._make(result)
