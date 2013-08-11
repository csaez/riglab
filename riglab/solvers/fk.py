from .base import Base
from ..manipulator import Manipulator
from .. import bonetools


class FK(Base):

    def custom_inputs(self):
        super(FK, self).custom_inputs()

    def custom_anim(self):
        super(FK, self).custom_build()
        anim = [Manipulator.new(parent=self.input.get("root"))]
        anim[0].owner = {"obj": self.obj, "class": self.classname}
        anim[0].icon.shape = "Box_Bone"
        # OPTIMIZATION: duplicate instead of create a new one
        copies = len(self.input.get("skeleton")) - 1
        anim.extend(anim[0].duplicate(copies))
        anim[0].icon.shape = "Pointed_Circle"
        # align
        data = zip(*bonetools.curve_data(self.helper.get("curve")))
        bonetools.align_matrix4(anim[0].zero, data[0][0])
        for i, (matrix, length) in enumerate(data[:-1]):
            m = anim[i + 1]
            m.set_parent(anim[i].anim)
            bonetools.align_matrix4(m.zero, matrix)
            m.icon.sclx = length
        # rename
        for i, each in enumerate(anim):
            each.rename(self.solvername, i)
            self.input.get("anim").append(each.anim)
            self.helper.get("hidden").extend([each.zero, each.space])
        self.input["anim"] = [x.anim for x in anim]

    def custom_build(self):
        super(FK, self).custom_build()
        for i, bone in enumerate(self.input.get("skeleton")[:-1]):
            self.output.get("snap_ref").append(bone)
            anim = self.input["anim"][i + 1]
            self.output["tm"][i].Kinematics.AddConstraint("Pose", anim)

    def validate(self):
        return len(self.input.get("skeleton")) > 1
