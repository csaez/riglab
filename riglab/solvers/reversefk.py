from .fk import FK


class ReverseFK(FK):

    def custom_build(self):
        skeleton = list(self.input.get("skeleton"))  # copy
        skeleton.reverse()
        for i, bone in enumerate(skeleton[:-1]):
            self.output.get("snap_ref").append(bone)
            anim = self.input["anim"][i + 1]
            self.output["tm"][i].Kinematics.AddConstraint("Pose", anim)

    def connect(self):
        for i, bone in enumerate(self.input.get("skeleton")[1:]):
            target = self.output.get("tm")[i]
            cns = bone.Kinematics.AddConstraint("Pose", target, True)
            for param in ("active", "blendweight"):
                expr = self.input.get(param).FullName
                cns.Parameters(param).AddExpression(expr)
