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
        anim[0].icon.shape = "Box_Bone2"  # TODO: replace by config file
        # OPTIMIZATION: duplicate instead of create a new one
        copies = len(self.input.get("skeleton")) - 2
        if copies >= 1:
            anim.extend(anim[0].duplicate(copies))
        # align
        data = zip(*bonetools.curve_data(self.helper.get("curve")))
        bonetools.align_matrix4(anim[0].zero, data[0][0])
        for i, (matrix, length) in enumerate(data[:-1]):
            m = anim[i]
            if i > 0:
                m.parent = anim[i - 1].anim
            bonetools.align_matrix4(m.zero, matrix)
            m.icon.sclx = length
        # rename
        for i, each in enumerate(anim):
            each.rename(self.name, i)
            self.input.get("anim").append(each.anim)
            self.helper.get("hidden").extend([each.zero, each.space])
        self.input["anim"] = [x.anim for x in anim]

    def custom_build(self):
        super(FK, self).custom_build()
        skeleton = self.input.get("skeleton")[:-1]
        if self.reversed():
            skeleton = self.input.get("skeleton")[1:]
        for i, bone in enumerate(skeleton):
            anim = self.input["anim"][i]
            self.output["tm"][i].Kinematics.AddConstraint("Pose", anim)
            # set snap reference
            self.get_manipulator(anim.FullName).snap_ref(bone)
        # connect root
        self.get_manipulator(self.input["anim"][0].FullName).snap_ref(
            self.input["skeleton"][0])

    @staticmethod
    def validate(skeleton):
        return len(skeleton) > 1
