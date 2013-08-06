from .base import Base
from ..manipulator import Manipulator


class FK(Base):

    def custom_inputs(self):
        super(FK, self).custom_inputs()

    def custom_build(self):
        super(FK, self).custom_build()
        anim = [Manipulator.create(parent=self.input.get("root"))]
        anim[0].icon.shape = "Box_Bone"
        # OPTIMIZATION: duplicate instead of create a new one
        copies = len(self.input.get("skeleton")) - 1
        anim.extend(anim[0].duplicate(copies))
        # restore manipulator settings
        anim[0].icon.shape = "Pointed_Circle"
        anim[0].align(self.input.get("skeleton")[0])
        for i, bone in enumerate(self.input.get("skeleton")[:-1]):
            m = anim[i + 1]
            m.icon.sclx = self.input.get("length")[i]
            m.set_parent(anim[i].anim)
            m.align(bone)
            self.output.get("snap_ref").append(bone)
            self.output["tm"][i].Kinematics.AddConstraint("Pose", m.anim)
        # rename
        for i, each in enumerate(anim):
            each.rename(self.solvername, i)
            self.input.get("anim").append(each.anim)
            self.helpers.get("hidden").extend([each.zero, each.space])
        # update data holder
        self.update()

    def validate(self):
        return len(self.input.get("skeleton")) > 1
