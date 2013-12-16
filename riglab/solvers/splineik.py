import os

from wishlib.si import si, siget

from .base import Base
from ..manipulator import Manipulator


class SplineIK(Base):

    def custom_anim(self):
        p0 = Manipulator.new(parent=self.input.get("root"))
        p0.owner = {"obj": self.obj, "class": self.classname}
        p1, p2, p3 = p0.duplicate(3)  # OPTIMIZATION
        for i, ctrl in enumerate((p0, p1, p2, p3)):
            ctrl.rename(self.name, i)
            if 0 < i < 3:
                ctrl.icon.size = 0.25
                continue
            ctrl.icon.shape = "Rounded_Square"
        p1.icon.connect = p0.anim
        p2.icon.connect = p3.anim
        # save anim components and cleanup
        for x in (p0, p1, p2, p3):
            self.input["anim"].append(x.anim)
            self.helper["hidden"].append(x.zero)
            self.helper["hidden"].append(x.space)
        # create a live bezier curve
        op = si.ApplyGenOp("CrvFit", "", self.helper["curve"])(0)
        op.Parameters("points").Value = 1
        self.helper["bezier"] = op.Parent3DObject
        self.helper["bezier"].Name = self.nm.qn(self.name, "bezierCurve")
        self.helper["root"].AddChild(self.helper["bezier"])
        self.helper["hidden"].append(self.helper.get("bezier"))
        pts = self.helper["bezier"].ActivePrimitive.Geometry.Points
        # align anim controls
        for i, pnt in enumerate(pts):
            zero = self.input["anim"][i].Parent
            tm = zero.Kinematics.Global.Transform
            tm.SetTranslation(pnt.Position)
            zero.Kinematics.Global.Transform = tm

    def custom_build(self):
        super(SplineIK, self).custom_build()
        # get paths
        cmp_dir = os.path.join(os.path.dirname(__file__), "..", "data",
                               "compounds")
        cmp_dir = os.path.normpath(cmp_dir)
        # ice rig
        cmp_file = os.path.join(cmp_dir, "riglab__SplineIKSolver.xsicompound")
        self.helper["ICERig"] = self.helper.get("root").AddNull()
        conn = ";".join([x.FullName for x in self.input["anim"]])
        ICEOp = si.ApplyICEOp(cmp_file, self.helper["ICERig"], conn)
        # set compound data
        compound = "{}.riglab__SplineIKSolver".format(ICEOp.FullName)
        curve_geo = self.helper["bezier"].ActivePrimitive.Geometry.Curves(0)
        siget(compound + ".Original_Length").Value = curve_geo.Length
        siget(compound + ".Size").Value = len(self.input["skeleton"])
        # apply transform
        cmp_file = os.path.join(cmp_dir, "riglab__ApplyTransform.xsicompound")
        for i, bone in enumerate(self.output["tm"]):
            ICEOp = si.ApplyICEOp(cmp_file, bone,
                                  self.helper["ICERig"].FullName)
            param = "{}.riglab__ApplyTransform.Index".format(ICEOp.FullName)
            siget(param).Value = i

    def connect(self):
        super(SplineIK, self).connect(compensate=False)

    def connect_reverse(self):
        super(SplineIK, self).connect_reverse(compensate=False)

    @staticmethod
    def validate(skeleton):
        return len(skeleton) > 3
