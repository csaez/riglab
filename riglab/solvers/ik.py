from wishlib.si import si, C

from .base import Base
from ..manipulator import Manipulator


class IK(Base):

    def custom_inputs(self):
        super(IK, self).custom_inputs()
        # add stretch parameter
        param = self.input.get("parameters")
        if not self.input.get("stretch"):
            self.input["stretch"] = param.AddParameter3("stretch", C.siBool, 1)

    def custom_build(self):
        super(IK, self).custom_build()
        # anim controls
        anim_root = Manipulator.new(parent=self.input.get("root"))
        anim_root.owner = {"obj": self.obj, "class": self.classname}
        anim_root.icon.shape = "Rounded_Square"
        anim_eff, anim_upv = anim_root.duplicate(2)  # OPTIMIZATION
        anim_eff.icon.connect = anim_root.anim
        anim_upv.icon.shape = "Rings"
        anim_upv.icon.size = 0.25
        anim_upv.icon.connect = self.input.get("skeleton")[1]
        for i, ctrl in enumerate((anim_root, anim_upv, anim_eff)):
            ctrl.rename(self.solvername, i)
            self.helpers.get("hidden").extend([ctrl.zero, ctrl.space])
        # setup
        root = self._ikchain()
        first_bone = root.Bones(0)
        anim_root.align(root)
        anim_upv.align(root.Bones(1))
        anim_eff.align(root.Effector)
        # offset anim upvector
        offset = -self.input.get("length")[0]
        si.Translate(anim_upv.zero, 0, offset, 0, "siRelative", "siLocal")
        # connect ikchain
        root.Kinematics.AddConstraint("Position", anim_root.anim)
        root.Effector.Kinematics.AddConstraint("Position", anim_eff.anim)
        for i, bone in enumerate(root.Bones):
            self.output.get("tm")[i].Kinematics.AddConstraint("Pose", bone)
        args = (first_bone.FullName, anim_upv.anim.FullName)
        si.ApplyOp("SkeletonUpVector", "{0};{1}".format(*args))
        first_bone.Properties("Kinematic Joint").Parameters("roll").Value = 180
        # stretching
        kwds = {"root": anim_root.anim,
                "eff": anim_eff.anim,
                "total_length": sum(self.input.get("length")),
                "stretch": self.input.get("stretch")}
        expr = "COND({stretch} == 1, MAX(ctr_dist({root}., {eff}.) / {total_length}, 1), 1)"
        expr = expr.format(**kwds)
        first_bone.Kinematics.Local.Parameters("sclx").AddExpression(expr)
        # update object members
        self.input["anim"] = (anim_root.anim, anim_upv.anim, anim_eff.anim)
        self.output["snap_ref"] = [self.input.get("skeleton")[0],
                                   self.input.get("skeleton")[0],
                                   self.input.get("skeleton")[-1]]
        self.update()

    def validate(self):
        return len(self.input.get("skeleton")) > 2

    def _ikchain(self):
        pos = [bone.Kinematics.Global.Transform.Translation.Get2()
               for bone in self.input.get("skeleton")]
        root = si.Create2DSkeleton(*list(pos[0] + pos[1]))
        root.Name = self.nm.qn(self.solvername + "Root", "jnt")
        root.Effector.Name = self.nm.qn(self.solvername + "Eff", "jnt")
        for i, position in enumerate(pos[2:]):
            bone = si.AppendBone(root.Effector, *position)
            # first bone
            if not i and bone.Kinematics.Local.Parameters("rotz").Value < 0:
                bone.Kinematics.Local.Parameters("rotz").Value *= -1
                root.Kinematics.Local.Parameters("rotx").Value += 180
        for i in range(root.Bones.Count):
            root.Bones(i).Name = self.nm.qn(self.solvername, "jnt", i)
        # align root with first bone
        first = root.Bones(0)
        root.Kinematics.Global.Transform = first.Kinematics.Global.Transform
        # cleanup
        self.helpers.get("root").AddChild(root)
        self.helpers.get("hidden").extend(list(root.Bones))
        self.helpers.get("hidden").extend([root, root.Effector])
        return root
