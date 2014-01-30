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
from math import pi
from collections import namedtuple

import naming
from wishlib.si import si, sisel, project_into_mesh, simath

from .joint import Joint

COMPOUND_DIR = os.path.join(os.path.dirname(__file__), "data", "compounds")


# HELPERS
def curve_data(curve):
    curvedata = os.path.join(COMPOUND_DIR, "riglab__SetCurveData.xsicompound")
    ICE = si.ApplyICEOp(curvedata, curve, "")
    geo = curve.ActivePrimitive.Geometry
    matrices = geo.GetICEAttributeFromName("TM").DataArray2D[0][0]
    lengths = geo.GetICEAttributeFromName("length").DataArray2D[0][0]
    si.DeleteObj(ICE)
    data = (matrices, list(lengths) + [0.0])
    return namedtuple("CurveData", "matrices, lengths")._make(data)


def rename_chain(chain, itemName, rule="3dobject"):
    nm = naming.Manager()
    nm.rule = rule
    chain.Root.Name = nm.qn(itemName + "Root", "jnt")
    chain.Root.Effector.Name = nm.qn(itemName + "Eff", "jnt")
    for i, bone in enumerate(chain.Root.Bones):
        bone.Name = nm.qn(itemName, "jnt", i)


def align_matrix4(obj, matrix):
    tm = obj.Kinematics.Global.Transform
    tm.SetMatrix4(matrix)
    obj.Kinematics.Global.Transform = tm


def deep(obj, d=0):
    if obj.Parent.FullName == si.ActiveSceneRoot.Name:
        return d
    return deep(obj.Parent, d + 1)


def _get_coord(meshes=None):
    # get meshes
    meshes = meshes or list()
    coord = si.PickPosition()
    if coord("ButtonPressed"):
        # get coord in screen space
        coord = [coord("Pos" + a) for a in "XYZ"]
        if si.GetKeyboardState()("Shift") == 2:  # CTRL key pressed
            return coord
        # raycast to meshes
        coords = filter(lambda x: x is not None,
                        [project_into_mesh(mesh, coord, 4) for mesh in meshes])
        coord = coords[0] if len(coords) else coord
        # return coord, raycast biased
        return coord
    return None


def draw_linear_curve(meshes=None):
    # collect meshes
    meshes = list(meshes) or list(sisel)
    # if not len(meshes):
    #     msj = "Please pick the polymesh you want to draw into."
    #     meshes = list()
    #     picked = si.PickElement(C.siPolyMeshFilter, msj)("PickedElement")
    #     while picked:
    #         if picked.FullName not in meshes:
    #             meshes.append(picked.FullName)
    #         picked = si.PickElement(C.siPolyMeshFilter, msj)("PickedElement")
    #     meshes = map(siget, meshes)
    # get initial point
    coord = _get_coord(meshes)
    if coord:
        # start drawing
        curve = si.SICreateCurve("crvlist", 1, 1)
        si.SelectObj(curve)
        while coord is not None:
            si.SIAddPointOnCurveAtEnd(curve, *coord)
            # get next point
            coord = _get_coord(meshes)
    return curve


def align2curve(objs, curve):
    for i, (matrix, length) in enumerate(zip(*curve_data(curve))):
        try:
            obj = objs[i]
        except IndexError:
            return
        align_matrix4(obj, matrix)
        Joint(obj, length=length, size=0.25)


def orthogonalize(obj):
    tm = obj.Kinematics.Global.Transform
    r = tm.Rotation
    v = simath.CreateVector3()
    r.GetXYZAngles(v)
    a = list()
    for x in v.Get2():
        a.append(pi / 2.0 * x / abs(x) if abs(x) > pi / 4.0 else 0)
    r.SetFromXYZAngles(simath.CreateVector3(*a))
    tm.SetRotation(r)
    obj.Kinematics.Global.Transform = tm


# CONVERTERS
def sel2curve(sel, parent=None):
    parent = parent or si.ActiveSceneRoot
    pos = [str(x.Kinematics.Global.Transform.Translation.Get2()) for x in sel]
    curve = si.SICreateCurve("crvlist", 1, 1)
    si.SISetCurvePoints(curve, ",".join(pos), False)
    parent.AddChild(curve)
    return curve


def sel2chain(nulls):
    curve = sel2curve(nulls)
    root = curve2chain(curve)
    si.DeleteObj(curve)
    return root


def curve2null(curve, parent=None):
    parent = parent or si.ActiveSceneRoot
    result = list()
    for matrix, length in zip(*curve_data(curve)):
        parent = parent.AddNull()
        align_matrix4(parent, matrix)
        Joint(parent, length=length, size=0.25)
        result.append(parent)
    return result


def curve2chain(curve, parent=None):
    parent = parent or si.ActiveSceneRoot
    data = curve_data(curve)
    pos = [x.Get2()[12:-1] for x in data.matrices]
    root = si.Create2DSkeleton(*list(pos[0] + pos[1]))
    root.Kinematics.Global.Transform = root.Bones(
        0).Kinematics.Global.Transform
    for i, position in enumerate(pos[2:]):
        si.AppendBone(root.Effector, *position)
    parent.AddChild(root)
    return root


def chain2null(chain, parent=None):
    parent = parent or si.ActiveSceneRoot
    result = list()
    root = chain.Root
    for bone in root.Bones:
        parent = parent.AddNull()
        parent.Kinematics.Global.Transform = bone.Kinematics.Global.Transform
        Joint(parent, length=bone.Parameters("length").Value, size=0.25)
        result.append(parent)
    result.append(parent.AddNull())
    result[-1].Kinematics.Global.Transform = root.Effector.Kinematics.Global.Transform
    return result
