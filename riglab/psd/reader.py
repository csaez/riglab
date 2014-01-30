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
from wishlib.si import si, siget

COMPOUND_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                             "..", "data", "compounds"))


class PoseReader(object):

    def __init__(self, obj):
        super(PoseReader, self).__init__()
        self.obj = obj


class ConeReader(PoseReader):
    COMPOUND_FILE = "riglab__ConeReader.xsicompound"
    COMPOUND = os.path.splitext(COMPOUND_FILE)[0]
    param_table = {"angle": "Angle",
                   "size": "Size",
                   "debug": "Debug",
                   "show_value": "Show_Value"}

    def __init__(self, *args, **kwds):
        super(ConeReader, self).__init__(*args, **kwds)
        self._ICE = self.obj.ActivePrimitive.ICETrees(self.COMPOUND)
        if not self._ICE:
            msj = "{} isnt a valid reader, operator not found."
            raise Exception(msj.format(self.obj))

    @classmethod
    def new(cls, target=None):
        obj = si.SIGetPrim("PointCloud")("Value")  # create an empty pcloud
        obj.Name = "poseReader"
        si.ApplyICEOp(os.path.join(COMPOUND_DIR, cls.COMPOUND_FILE), obj, " ")
        reader = cls(obj)
        if target:
            reader.target = target
            # align to target
            reader.obj.Kinematics.Global.Transform = target.Kinematics.Global.Transform
        return reader

    def __setattr__(self, attr, value):
        super(ConeReader, self).__setattr__(attr, value)
        param = self.param_table.get(attr)
        if param:
            self._setvalue(param, value)

    def __getattr__(self, attr):
        param = self.param_table.get(attr)
        if param:
            return self._getvalue(param)
        return super(ConeReader, self).__getattr__(attr)

    @property
    def target(self):
        value = self._getvalue("SceneReferenceNode.reference", False)
        return siget(value)

    @target.setter
    def target(self, value):
        self._setvalue("SceneReferenceNode.reference", value.FullName, False)

    def show(self):
        si.InspectObj(".".join([self._ICE.FullName, self.COMPOUND]))

    def _setvalue(self, param, value, compound=True):
        base = [self._ICE.FullName]
        if compound:
            base.append(self.COMPOUND)
        base.append(param)
        siget(".".join(base)).Value = value

    def _getvalue(self, param, compound=True):
        base = [self._ICE.FullName]
        if compound:
            base.append(self.COMPOUND)
        base.append(param)
        return siget(".".join(base)).Value
