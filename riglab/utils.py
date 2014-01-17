import os
from collections import namedtuple

from wishlib.si import si, siget

from .joint import Joint
from . import naming

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


def project_into_mesh(curve, mesh=None):
    COMPOUND = "riglab__ProjectIntoMesh"
    fp = os.path.join(COMPOUND_DIR, COMPOUND + ".xsicompound")
    # apply ice op
    o = si.ApplyICEOp(fp, curve, "")
    cmp_name = o.FullName + "." + COMPOUND
    # add a port per each curve's point
    for _ in range(1, curve.ActivePrimitive.Geometry.Points.Count):
        si.AddPortToICENode(
            cmp_name + ".MaxDepth1", "siNodePortDataInsertionLocationAfter")
    # set defaults
    si.SetValue(cmp_name + ".MaxDepth*", 1)
    mesh = mesh or si.PickObject()("PickedElement")
    siget(cmp_name + ".Reference").Value = mesh.FullName
    # inspect
    if siget("preferences.Interaction.autoinspect").Value:
        si.InspectObj(cmp_name)


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
