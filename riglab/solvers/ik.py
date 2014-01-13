from wishlib.si import si, C

from .base import Base
from ..manipulator import Manipulator
from .. import bonetools


class IK(Base):

    def custom_inputs(self):
        super(IK, self).custom_inputs()
        # add stretch parameter
        param = self.input.get("parameters")
        if not self.input.get("stretch"):
            self.input["stretch"] = param.AddParameter3("stretch", C.siBool, 1)

    def custom_anim(self):
        # create
        anim_root = Manipulator.new(parent=self.input.get("root"))
        anim_root.owner = {"obj": self.obj, "class": self.classname}
        anim_root.icon.shape = "Rounded_Square"
        anim_eff, anim_upv = anim_root.duplicate(2)  # OPTIMIZATION
        anim_eff.icon.connect = anim_root.anim
        anim_upv.icon.shape = "Rings"
        anim_upv.icon.size = 0.25
        anim_upv.icon.connect = self.input.get("skeleton")[1]
        for i, ctrl in enumerate((anim_root, anim_upv, anim_eff)):
            ctrl.rename(self.name, i)
            self.helper.get("hidden").extend([ctrl.zero, ctrl.space])
        # align
        data = bonetools.curve_data(self.helper["curve"])
        bonetools.align_matrix4(anim_root.zero, data[0][0])
        bonetools.align_matrix4(anim_eff.zero, data[0][-1])
        bonetools.align_matrix4(anim_upv.zero, data[0][1])
        si.Translate(anim_upv.zero, 0, -data[1][0], 0, "siRelative", "siLocal")
        # save attributes
        self.input["anim"] = (anim_root.anim, anim_upv.anim, anim_eff.anim)

    def custom_build(self):
        super(IK, self).custom_build()
        # setup
        root = self._ikchain()
        # connect ikchain
        root.Kinematics.AddConstraint("Position", self.input["anim"][0])
        root.Effector.Kinematics.AddConstraint(
            "Position", self.input["anim"][-1])
        for i, bone in enumerate(root.Bones):
            self.output.get("tm")[i].Kinematics.AddConstraint("Pose", bone)
        first_bone = root.Bones(0)
        args = (first_bone.FullName, self.input["anim"][1].FullName)
        si.ApplyOp("SkeletonUpVector", "{0};{1}".format(*args))
        first_bone.Properties("Kinematic Joint").Parameters("roll").Value = 180
        # stretching
        kwds = {"root": self.input["anim"][0].FullName,
                "eff": self.input["anim"][-1].FullName,
                "total_length": sum(bonetools.curve_data(self.helper["curve"])[1]),
                "stretch": self.input.get("stretch").FullName}
        expr = "COND({stretch} == 1, MAX(ctr_dist({root}., {eff}.) / {total_length}, 1), 1)"
        expr = expr.format(**kwds)
        first_bone.Kinematics.Local.Parameters("sclx").AddExpression(expr)
        # set snap reference
        self.get_man(self.input["anim"][0]).snap_ref(self.input["skeleton"][0])
        self.get_man(self.input["anim"][1]).snap_ref(self.input["skeleton"][0])
        self.get_man(self.input["anim"][2]).snap_ref(
            self.input["skeleton"][-1])

    def _ikchain(self):
        root = bonetools.curve2chain(self.helper.get("curve"),
                                     parent=self.helper["root"])
        # rename
        root.Name = self.nm.qn(self.name + "Root", "jnt")
        root.Effector.Name = self.nm.qn(self.name + "Eff", "jnt")
        for i in range(root.Bones.Count):
            root.Bones(i).Name = self.nm.qn(self.name, "jnt", i)
        # cleanup
        self.helper.get("hidden").extend(list(root.Bones))
        self.helper.get("hidden").extend([root, root.Effector])
        return root

    @staticmethod
    def validate(skeleton):
        return len(skeleton) >= 2
