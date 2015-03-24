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
from wishlib.si import si, siget, simath, SIWrapper, sianchor
from wishlib.qt import set_style

from . import utils
from .layout.pose_space import PoseSpace


class Manipulator(SIWrapper):
    nm = naming.Manager()
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
    PROP_NAME = "Manipulator_Data"
    SPACE_TYPES = ("reader", "orient", "parent")

    def __init__(self, obj):
        self.spaces = {x: dict() for x in self.SPACE_TYPES}
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
        super(Manipulator, self).__init__(obj, self.PROP_NAME)
        self._mute = False
        self.anim = obj
        self.icon = Icon(self.anim)
        self.zero = self.anim.Parent
        self.orient = self.zero.Parent
        self.space = self.orient.Parent
        for x in self.SPACE_TYPES:
            if not self.spaces.get(x):
                self.spaces[x] = dict()

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
        return [x for s in self.SPACE_TYPES for x in self.spaces[s].keys()]

    def reset_spaces(self):
        for space_type, space_data in self.spaces.iteritems():
            for name, cns in space_data.iteritems():
                d = self._offsets.get(name)
                if not d:
                    continue
                for p, v in d.iteritems():
                    cns.Parameters(p).Value = v
        self.zero.Kinematics.Local.Transform = simath.CreateTransform()

    def add_space(self, name=None, target=None, space_type="parent"):
        space_type = space_type.lower()
        if not target or space_type not in self.SPACE_TYPES:
            return
        print "ready!"
        # validate name
        name = name or target.Name
        if name in self.list_spaces():
            return
        # add cns
        tm = self.zero.Kinematics.Global.Transform
        cns = {"parent": self._parent, "orient":
               self._orient, "reader": self._pose}.get(space_type)(target)
        self.spaces[space_type][name] = cns
        # save offset
        if space_type != "reader":
            self._offsets[name] = {p + a: cns.Parameters(p + a).Value
                                   for p in ("scl", "rot", "pos") for a in "xyz"}
        # restore transforms
        self.zero.Kinematics.Global.Transform = tm
        self.active_space = name
        self.update()  # update metadata

    def _parent(self, target):
        cns = self.space.Kinematics.AddConstraint("Pose", target, True)
        return cns

    def _orient(self, target):
        cns = self.orient.Kinematics.AddConstraint("Pose", target, True)
        cns.Parameters("cnspos").Value = False
        cns.Parameters("cnsscl").Value = False
        return cns

    def _pose(self, target):
        cmp_name = "riglab__ConstraintByReader"
        cmp_file = os.path.join(self.DATA_DIR, "compounds",
                                cmp_name + ".xsicompound")
        op = si.SIApplyICEOp(cmp_file, self.orient, target.FullName)
        cmp = siget(op.FullName + "." + cmp_name)
        base_name = str(cmp.FullName) + "."
        mapping = {"scl": "Scaling_", "rot":
                   "Rotation_", "pos": "Translation_"}
        for x in ("First_", "Second_"):
            for k, v in mapping.iteritems():
                for a in "xyz":
                    val = self.anim.Kinematics.Global.Parameters(k + a).Value
                    siget(base_name + x + v + a).Value = val
        siget(base_name + "active").Value = True
        return cmp

    def remove_space(self, name):
        for space_type, data in self.spaces.iteritems():
            cns = data.get(name)
            if not cns:
                continue
            si.DeleteObj(cns)
            del self.spaces[space_type][name]
            self.update()

    def inspect_space(self, space_name):
        for space_type, data in self.spaces.iteritems():
            if not data.get(space_name):
                continue
            space = data.get(space_name)
            if space_type == "reader":
                win = PoseSpace(space, self, parent=sianchor())
                set_style(win, True)
                win.show()
            else:
                si.InspectObj(space)

    @property
    def active_space(self):
        # it has to be live because of animation
        _active_space = "default"
        for x in self.SPACE_TYPES:
            for name, cns in self.spaces[x].iteritems():
                if siget(cns.FullName + ".active").Value:
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
                siget(cns.FullName + ".active").Value = name == k
        self.zero.Kinematics.Global.Transform = tm

    def rename(self, *args, **kwds):
        with self.nm.override(rule="3dobject"):
            self.space.Name = self.nm.qn("group", *args, **kwds)
            self.zero.Name = self.nm.qn("zero", *args, **kwds)
            self.anim.Name = self.nm.qn("anim", *args, **kwds)
            args = [x + "-orient" if type(x) == str else x for x in args]
            self.orient.Name = self.nm.qn("rig", *args, **kwds)
        self.update()

    def destroy(self):
        for child in self.anim.Children:
            self.space.AddChild(child)
        for x in (self.anim, self.zero, self.orient, self.space):
            si.DeleteObj(x)

    def align(self, dst, component="space"):
        if hasattr(self, component):
            src = getattr(self, component)
            src.Kinematics.Global.Transform = dst.Kinematics.Global.Transform

    def align_matrix4(self, m4, component="space"):
        if hasattr(self, component):
            src = getattr(self, component)
            utils.align_matrix4(src, m4)

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
        cns = self.spaces["parent"].get(self.active_space) or self.spaces[
            "orient"].get(self.active_space)
        siget(p + ".Reference").Value = cns.Constraining(0).FullName
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
        self._invert = value
        value = (-1.0, 180) if value else (1.0, 0)
        for a in "xyz":
            self.zero.Kinematics.Local.Parameters("nscl" + a).Value = value[0]
        self.zero.Kinematics.Local.Parameters("nrotz").Value = value[1]
