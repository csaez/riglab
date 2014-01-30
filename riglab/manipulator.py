# This file is part of riglab.
# Copyright (C) 2014  Cesar Saez

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

import naming
from rigicon.icon import Icon
from wishlib.si import si, siget, simath, SIWrapper

from . import utils


class Manipulator(SIWrapper):
    nm = naming.Manager()
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

    def __init__(self, obj):
        self.spaces = dict()
        self._visibility = True
        self.owner = {"obj": None, "class": None}
        self._snap_ref = {"obj": None,
                          "offset": (1, 0, 0, 0,
                                     0, 1, 0, 0,
                                     0, 0, 1, 0,
                                     0, 0, 0, 1)}
        super(Manipulator, self).__init__(obj, "Manipulator_Data")
        self.anim = obj
        self.icon = Icon(self.anim)
        self.zero = self.anim.Parent
        self.space = self.zero.Parent

    @classmethod
    def new(cls, parent=None):
        if parent is None:
            parent = si.ActiveSceneRoot
        space = parent.AddNull()
        zero = space.AddNull()
        icon = Icon.new()
        anim = icon.obj
        zero.AddChild(anim)
        manipulator = cls(anim)
        return manipulator

    def add_space(self, name=None, target=None):
        if not target:
            return
        name = name or target.Name
        tm = self.zero.Kinematics.Global.Transform
        cns = self.space.Kinematics.AddConstraint("Pose", target, True)
        self.spaces[name] = cns
        self.zero.Kinematics.Global.Transform = tm
        self.active_space = name
        self.update()

    def remove_space(self, name):
        cns = self.spaces.get(name)
        if cns is not None:
            si.DeleteObj(cns)
            del self.spaces[name]
            self.update()

    @property
    def active_space(self):
        for name, cns in self.spaces.iteritems():
            if cns and cns.Parameters("active").Value:
                return name
        return "default"

    @active_space.setter
    def active_space(self, name):
        tm = self.zero.Kinematics.Global.Transform
        for k, cns in self.spaces.iteritems():
            if cns is not None:
                cns.Parameters("active").Value = name == k
        self.zero.Kinematics.Global.Transform = tm

    def rename(self, *args, **kwds):
        with self.nm.override(rule="3dobject"):
            self.space.Name = self.nm.qn("group", *args, **kwds)
            self.zero.Name = self.nm.qn("zero", *args, **kwds)
            self.anim.Name = self.nm.qn("anim", *args, **kwds)
        self.update()

    def destroy(self):
        for child in self.anim.Children:
            self.space.AddChild(child)
        for x in (self.anim, self.zero, self.space):
            si.DeleteObj(x)

    def align(self, dst, component="zero"):
        if hasattr(self, component):
            src = getattr(self, component)
            src.Kinematics.Global.Transform = dst.Kinematics.Global.Transform

    def neutral_pose(self):
        self.zero.Kinematics.Global.Transform = self.anim.Kinematics.Global.Transform

    def duplicate(self, number=1):
        results = list()
        copies = si.Duplicate((self.space, self.zero, self.anim), number)
        for i in range(number):
            i *= 3
            self.space.Parent.AddChild(copies[i + 0])
            copies[i + 0].AddChild(copies[i + 1])
            copies[i + 1].AddChild(copies[i + 2])
            results.append(self.__class__(copies[i + 2]))
        return results

    @property
    def parent(self):
        return self.space.Parent

    @parent.setter
    def parent(self, obj):
        if obj:
            obj.AddChild(self.space)
            self.update()

    def snap_ref(self, ref):
        m4 = self.zero.Kinematics.Global.Transform.Matrix4
        refM4 = ref.Kinematics.Global.Transform.Matrix4
        refM4.InvertInPlace()
        m4.MulInPlace(refM4)
        self._snap_ref = {"obj": ref, "offset": m4.Get2()}

    def snap(self):
        obj = self._snap_ref.get("obj")
        if obj is not None:
            m4 = simath.CreateMatrix4(*self._snap_ref["offset"])
            m4.MulInPlace(obj.Kinematics.Global.Transform.Matrix4)
            utils.align_matrix4(self.anim, m4)

    @property
    def debug(self):
        return siget(self._debug_prop() + ".Debug").Value

    @debug.setter
    def debug(self, value):
        p = self._debug_prop()
        siget(p + ".Reference").Value = self.active_space
        siget(p + ".Debug").Value = value

    def _debug_prop(self):
        cmp_name = "riglab__ActiveSpace"
        cmp_file = os.path.join(self.DATA_DIR, "compounds",
                                cmp_name + ".xsicompound")
        ICEOp = self.anim.ActivePrimitive.ICETrees.Find(cmp_name)
        if not ICEOp:
            ICEOp = si.SIApplyICEOp(cmp_file, self.anim, "")
        return ICEOp.FullName + "." + cmp_name

    @property
    def visibility(self):
        return self._visibility

    @visibility.setter
    def visibility(self, value):
        self._visibility = value
