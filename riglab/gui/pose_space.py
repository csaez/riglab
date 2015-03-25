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

from wishlib.si import siget
from wishlib.qt import QtGui, loadUi, set_style

from ..psd.reader import ConeReader


class PoseSpace(QtGui.QDialog):
    TABLE = {"sclx": "Second_Scaling_x",
             "scly": "Second_Scaling_y",
             "sclz": "Second_Scaling_z",
             "rotx": "Second_Rotation_x",
             "roty": "Second_Rotation_y",
             "rotz": "Second_Rotation_z",
             "posx": "Second_Translation_x",
             "posy": "Second_Translation_y",
             "posz": "Second_Translation_z"}

    def __init__(self, cmp, manip, parent=None):
        super(PoseSpace, self).__init__(parent)
        self.cmp = cmp
        self.manip = manip
        self._mute = False
        self.setup_ui()
        reader = siget(
            ".".join(self.cmp.FullName.split(".")[:-1]) + ".SceneReferenceNode.reference").Value
        self.ui.reader.setText(reader)
        self.ui.inspect.clicked.connect(
            lambda: ConeReader(siget(reader)).show())
        self.ui.active.toggled.connect(
            lambda x, p=siget(cmp.FullName + ".active"): self.set_value(p, x))
        for k, v in self.TABLE.iteritems():
            item = getattr(self.ui, k)
            param = siget(cmp.FullName + "." + v)
            item.setValue(param.Value)
            item.valueChanged.connect(
                lambda x, p=param: self.set_value(p, float(x)))
        self.ui.set_pose.clicked.connect(self.pose_clicked)

    def setup_ui(self):
        icons = dict()
        images = {"pick": "iconmonstr-cursor-touch-icon-256.png",
                  "show": "iconmonstr-menu-2-icon-256.png"}
        ui_dir = os.path.join(os.path.dirname(__file__), "ui")
        self.ui = loadUi(os.path.join(ui_dir, "pose_space.ui"), self)
        for k, v in images.iteritems():
            icons[k] = QtGui.QIcon(os.path.join(ui_dir, "images", v))
        # self.ui.pick.setIcon(icons.get("pick"))
        self.ui.inspect.setIcon(icons.get("show"))

    def set_value(self, param, value):
        if not self._mute:
            param.Value = float(value)

    def pose_clicked(self):
        # self._mute = True
        kine = self.manip.anim.Kinematics.Global
        tm = kine.Transform
        values = [kine.Parameters(k).Value for k in self.TABLE.keys()]
        for i, (k, v) in enumerate(self.TABLE.iteritems()):
            item = getattr(self.ui, k)
            item.setValue(values[i])
        self.manip.anim.Kinematics.Global.Transform = tm
        # self._mute = False

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    win = PoseSpace()
    set_style(win, True)
    win.show()
    app.exec_()
