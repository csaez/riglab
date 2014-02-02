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

import naming
from rigicon.icon import Icon
from wishlib.si import si, siget, simath, SIWrapper

from . import utils


class Manipulator(SIWrapper):
    nm = naming.Manager()
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

    def __init__(self, obj):
        self.spaces = {"parent": dict(), "orient": dict()}
        self._offsets = dict()
        self._visibility = True
        self.owner = {"obj": None, "class": None}
        self._snap_ref = {"obj": None,
                          "offset": (1, 0, 0, 0,
                                     0, 1, 0, 0,
                                     0, 0, 1, 0,
                                     0, 0, 0, 1)}
        self._invert = False
        self._mute = True
        super(Manipulator, self).__init__(obj, "Manipulator_Data")
        self._mute = False
        self.anim = obj
        self.icon = Icon(self.anim)
        self.zero = self.anim.Parent
        self.orient = self.zero.Parent
        self.space = self.orient.Parent

    @classmethod
    def new(cls, parent=None):
        if parent is None:
            parent = si.ActiveSceneRoot
        space = parent.AddNull()
        orient = space.AddNull()
        zero = orient.AddNull()
        icon = Icon.new()
        anim = icon.obj
        zero.AddChild(anim)
        manipulator = cls(anim)
        return manipulator

    def list_spaces(self):
        return [x for s in ("parent", "orient") for x in self.spaces[s].keys()]

    def reset_spaces(self):
        for space_type, space_data in self.spaces.iteritems():
            for name, cns in space_data.iteritems():
                d = self._offsets.get(name)
                if not d:
                    continue
                for p, v in d.iteritems():
                    cns.Parameters(p).Value = v

    def add_space(self, name=None, target=None, space_type="parent"):
        if not target or space_type.lower() not in ("parent", "orient"):
            return
        # validate name
        name = name or target.Name
        if name in self.list_spaces():
            print "ERROR: invalid name"
            return
        # add cns
        tm = self.zero.Kinematics.Global.Transform
        if space_type == "parent":
            cns = self.space.Kinematics.AddConstraint("Pose", target, True)
        else:
            cns = self.orient.Kinematics.AddConstraint("Pose", target, True)
            cns.Parameters("cnspos").Value = False
            cns.Parameters("cnsscl").Value = False
        self.spaces[space_type.lower()][name] = cns
        # save offset
        self._offsets[name] = {p + a: cns.Parameters(p + a).Value
                               for p in ("scl", "rot", "pos") for a in "xyz"}
        # restore transforms
        self.zero.Kinematics.Global.Transform = tm
        self.active_space = name
        self.update()  # update metadata

    def remove_space(self, name):
        for space_type, data in self.spaces.iteritems():
            cns = data.get(name)
            if not cns:
                continue
            si.DeleteObj(cns)
            del self.spaces[space_type][name]
            self.update()

    @property
    def active_space(self):
        # it has to be live because of animation
        _active_space = "default"
        for x in ("parent", "orient"):
            for name, cns in self.spaces[x].iteritems():
                if cns.Parameters("active").Value:
                    _active_space = name
        return _active_space

    @active_space.setter
    def active_space(self, name):
        if self._mute:
            return
        spaces = self.spaces
        if name in self.spaces["orient"].keys():
            spaces = self.spaces.copy()
            del spaces["parent"]  # exclude parent
        tm = self.zero.Kinematics.Global.Transform
        for space_type, data in spaces.iteritems():
            for k, cns in data.iteritems():
                cns.Parameters("active").Value = name == k
        self.zero.Kinematics.Global.Transform = tm

    def rename(self, *args, **kwds):
        with self.nm.override(rule="3dobject"):
            self.space.Name = self.nm.qn("group", *args, **kwds)
            self.orient.Name = self.nm.qn("rig", *args, **kwds)
            self.zero.Name = self.nm.qn("zero", *args, **kwds)
            self.anim.Name = self.nm.qn("anim", *args, **kwds)
        self.update()

    def destroy(self):
        for child in self.anim.Children:
            self.space.AddChild(child)
        for x in (self.anim, self.zero, self.orient, self.space):
            si.DeleteObj(x)

    def align(self, dst, component="orient"):
        if hasattr(self, component):
            src = getattr(self, component)
            src.Kinematics.Global.Transform = dst.Kinematics.Global.Transform

    def neutral_pose(self):
        self.orient.Kinematics.Global.Transform = self.zero.Kinematics.Global.Transform = self.anim.Kinematics.Global.Transform

    def duplicate(self, number=1):
        results = list()
        copies = si.Duplicate((self.space, self.orient, self.zero, self.anim),
                              number)
        for i in range(number):
            i *= 4
            self.space.Parent.AddChild(copies[i + 0])
            copies[i + 0].AddChild(copies[i + 1])
            copies[i + 1].AddChild(copies[i + 2])
            copies[i + 2].AddChild(copies[i + 3])
            results.append(self.__class__(copies[i + 3]))
        return results

    @property
    def parent(self):
        return self.space.Parent

    @parent.setter
    def parent(self, obj):
        if obj and not self._mute:
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
        if self._mute:
            return
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
        if self._mute:
            return
        self._visibility = value

    @property
    def invert(self):
        return self._invert

    @invert.setter
    def invert(self, value):
        if self._mute:
            return
        value = -1.0 if value else 1.0
        for a in "xyz":
            self.zero.Kinematics.Local.Parameters("scl" + a).Value = value
        self._invert = value
