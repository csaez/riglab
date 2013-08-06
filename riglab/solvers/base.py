from wishlib.si import si, siget, C, SIWrapper

from .. import naming


class Base(SIWrapper):
    nm = naming.Manager()
    nm.rule = "3dobject"

    def __init__(self, obj, name=None):
        self.classname = self.__class__.__name__
        self.solvername = name or self.classname
        self.input = {"root": None,
                      "parameters": None,
                      "active": None,
                      "blendweight": None,
                      "skeleton": list(),
                      "anim": list(),
                      "length": list()}
        self.output = {"root": None,
                       "tm": list(),
                       "snap_ref": list()}
        self.hidden = list()
        super(Base, self).__init__(obj, "Solver_Data")

    def build(self, skeleton):
        self.input["skeleton"] = list(skeleton)
        if not self.validate():
            return
        limit = len(self.input.get("skeleton")) - 1
        for i, bone in enumerate(self.input.get("skeleton")):
            # set bone params
            for param in ("cnsscl", "pivotactive", "pivotcompactive"):
                bone.Kinematics.Local.Parameters(param).Value = False
            if i < limit:
                # set outputs
                name = self.nm.qn(self.solvername, i, "rig")
                self.output["tm"].append(self.output.get("root").AddNull(name))
                # calc length
                next = self.input.get("skeleton")[i + 1]
                self.input.get("length").append(self.get_distance(bone, next))
        self.hidden.extend(self.output.get("tm"))
        self.custom_inputs()  # input custom parameters
        self.custom_build()  # solver implementation
        self.connect()
        self.style()

    def custom_inputs(self):
        # parameters
        if not self.input.get("parameters"):
            self.input["parameters"] = self.input[
                "root"].AddCustomProperty("Input_Parameters")
        # active
        if not self.input.get("active"):
            self.input["active"] = self.input[
                "parameters"].AddParameter3("active", C.siBool, True)
        # blendweight
        if not self.input.get("blendweight"):
            self.input["blendweight"] = self.input[
                "parameters"].AddParameter3("blendweight", C.siFloat, 1, 0, 1)
        # extend this method to suit solver needs
        pass

    def custom_build(self):
        # raise NotImplementedError()
        pass

    def validate(self):
        # raise NotImplementedError()
        return True

    def connect(self):
        for i, bone in enumerate(self.input.get("skeleton")[:-1]):
            target = self.output.get("tm")[i]
            cns = bone.Kinematics.AddConstraint("Pose", target)
            for param in ("active", "blendweight"):
                expr = self.input.get(param).FullName
                cns.Parameters(param).AddExpression(expr)

    def style(self):
        for x in self.hidden:
            x.Properties("Visibility").Parameters("viewvis").Value = False

    @property
    def state(self):
        if self.input.get("active"):
            return self.input.get("active").Value
        return None

    @state.setter
    def state(self, value):
        if self.input.get("active"):
            self.input.get("active").Value = value

    @staticmethod
    def get_distance(src, dst):
        v = dst.Kinematics.Global.Transform.Translation
        v.SubInPlace(src.Kinematics.Global.Transform.Translation)
        return v.Length()

    @classmethod
    def create(cls, skeleton, name=None):
        # solver objs
        obj = si.ActiveSceneRoot.AddNull()
        solver = cls(obj, name=name)
        solver.output["root"] = obj.AddNull()
        solver.input["root"] = obj.AddNull()
        # rename
        solver.obj.Name = cls.nm.qn(solver.solvername + "Solver", "group")
        solver.output["root"].Name = cls.nm.qn(solver.solvername +
                                               "Output", "group")
        solver.input["root"].Name = cls.nm.qn(solver.solvername +
                                              "Input", "group")
        # add to hidden list
        solver.hidden.extend([solver.obj,
                              solver.input.get("root"),
                              solver.output.get("root")])
        # build
        solver.build(skeleton)
        solver.update()  # update mutable data serialization
        return solver

    @classmethod
    def from_name(cls, name):
        obj = siget(name)
        return cls(obj)
