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

from wishlib.si import si, sisel
from wishlib.qt import QtGui

from .space_name import SpaceName
from ..manipulator import Manipulator
from ..rig import Rig
from .. import solvers
from .. import cache


def get_rig(obj):
    name = obj.FullName
    if not hasattr(cache, "rig"):
        cache.rig = dict()
    r = cache.rig.get(name)
    if not r:
        r = Rig(obj)
        cache.rig[name] = r
    return r


def get_manip(obj):
    name = obj.FullName
    if not hasattr(cache, "manip"):
        cache.manip = dict()
    m = cache.manip.get(name)
    if not m:
        m = Manipulator(obj)
        cache.manip[name] = m
    return m


def get_solver(obj, solver_class):
    name = obj.FullName
    if not hasattr(cache, "solver"):
        cache.solver = dict()
    s = cache.solver.get(name)
    if not s:
        s = getattr(solvers, solver_class)(obj)
        cache.solver[name] = s
    return s


class QuickLab(QtGui.QMenu):
    IMAGES = {"check": "iconmonstr-check-mark-icon-256.png", }
    for k, v in IMAGES.iteritems():
        IMAGES[k] = os.path.join(os.path.dirname(__file__), "ui", "images", v)

    def __init__(self, parent):
        super(QuickLab, self).__init__(parent)
        self.get_data()
        self.setup_ui()

    def get_data(self):
        o = sisel(0)
        self.manip = get_manip(o)
        if not self.manip:
            return
        self.rig = get_rig(o.Model)  # get rig
        if not self.rig:
            return
        # spaces
        self.spaces = self.manip.list_spaces()
        self.active_space = self.manip.active_space
        # states
        d = self.manip.owner
        s = get_solver(d.get("obj"), d.get("class"))
        for k, v in self.rig.groups.iteritems():
            if s.id in v.get("solvers"):
                self.group = k
                self.states = v.get("states").keys()
                self.active_state = self.rig.groups[k]["active"]

    def setup_ui(self):
        icon = (QtGui.QIcon(), QtGui.QIcon(self.IMAGES.get("check")))
        # space switching
        s = self.addMenu("Spaces")
        for x in self.spaces:
            a = s.addAction(x)
            a.setIcon(icon[int(x == self.active_space)])
            a.triggered.connect(lambda b, n=x: self.set_space(n))
        s.addSeparator()
        len_sp = len(self.spaces)
        s.addAction("New...").triggered.connect(lambda x: self.new_space())
        if len_sp:
            s.addAction("Remove...").triggered.connect(
                lambda x: self.remove_space())
            if len_sp > 1:
                s.addAction("Reset").triggered.connect(
                    lambda x: self.manip.reset_spaces())
            s.addAction("Inspect...").triggered.connect(
                lambda x: self.inspect_spaces())
        # states
        for x in self.states:
            a = self.addAction(x)
            a.setIcon(icon[int(x == self.active_state)])
            a.triggered.connect(lambda b, n=x: self.set_state(n))

    def set_state(self, name):
        self.rig.apply_state(self.group, name, snap=True)

    def set_space(self, name):
        self.manip.active_space = name

    def new_space(self):
        picked = si.PickObject()("PickedElement")
        if picked:
            ok, data = SpaceName.get_data(parent=self, space_name="")
            if ok:
                self.manip.add_space(name=data.name, target=picked,
                                     space_type=data.type)

    def remove_space(self):
        n, ok = QtGui.QInputDialog.getItem(self, "Remove Space", "Spaces:",
                                           self.spaces, 0, False)
        if ok:
            self.manip.remove_space(str(n))

    def inspect_spaces(self):
        n, ok = QtGui.QInputDialog.getItem(self, "Inspect Space", "Spaces:",
                                           self.spaces, 0, False)
        if ok:
            self.manip.inspect_space(str(n))
