from collections import namedtuple
from os import path
from wishlib.si import si

from . import naming

COMPOUND_DIR = path.join(path.dirname(__file__), "data", "compounds")


# HELPERS
def curve_data(curve):
    curvedata = path.join(COMPOUND_DIR, "riglab__SetCurveData.xsicompound")
    ICE = si.ApplyICEOp(curvedata, curve, "")
    geo = curve.ActivePrimitive.Geometry
    matrices = geo.GetICEAttributeFromName("TM").DataArray2D[0][0]
    lengths = geo.GetICEAttributeFromName("length").DataArray2D[0][0]
    si.DeleteObj(ICE)
    data = (matrices, list(lengths) + [None])
    return namedtuple("CurveData", "matrices, lengths")._make(data)


def style_null(null, length):
    null.Parameters("primary_icon").Value = 0
    null.Parameters("shadow_icon").Value = 4
    null.Parameters("shadow_offsetX").Value = length / 2
    null.Parameters("shadow_scaleX").Value = length
    null.Parameters("shadow_scaleY").Value = 0.25
    null.Parameters("shadow_scaleZ").Value = 0.25


def rename_chain(chain, itemName, rule="3dobject"):
    nm = naming.Manager()
    nm.rule = rule
    chain.Root.Name = nm.qn(itemName + "Root", "jnt")
    chain.Root.Effector.Name = nm.qn(itemName + "Eff", "jnt")
    for i, bone in enumerate(chain.Root.Bones):
        bone.Name = nm.qn(itemName, "jnt", i)


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
        tm = parent.Kinematics.Global.Transform
        tm.SetMatrix4(matrix)
        parent.Kinematics.Global.Transform = tm
        if length:
            style_null(parent, length)
        result.append(parent)
    return result


def curve2chain(curve, parent=None):
    parent = parent or si.ActiveSceneRoot
    data = curve_data(curve)
    pos = [x.Get2()[12:-1] for x in data.matrices]
    root = si.Create2DSkeleton(*list(pos[0] + pos[1]))
    for i, position in enumerate(pos[2:]):
        si.AppendBone(root.Effector, *position)
    return root


def chain2null(chain, parent=None):
    parent = parent or si.ActiveSceneRoot
    result = list()
    root = chain.Root
    for bone in root.Bones:
        parent = parent.AddNull()
        parent.Kinematics.Global.Transform = bone.Kinematics.Global.Transform
        style_null(parent, bone.Parameters("length").Value)
        result.append(parent)
    result.append(parent.AddNull())
    result[-1].Kinematics.Global.Transform = root.Effector.Kinematics.Global.Transform
    return result
