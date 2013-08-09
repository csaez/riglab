from wishlib.si import si, siget, C, SIWrapper, sianchor
from wishlib.qt.QtGui import QProgressDialog

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
        self.helpers = {"root": None,
                        "hidden": list()}
        super(Base, self).__init__(obj, "Solver_Data")

        # progress bar
        self.pb = QProgressDialog(sianchor())
        self.pb.setMinimum(0)
        self.pb.setMaximum(100)

    def build(self, skeleton):
        self.input["skeleton"] = list(skeleton)
        if not self.validate():
            return

        # init
        self.pb.show()
        self.pb.setLabelText("Init solver")
        self.pb.setValue(20)
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
        self.helpers.get("hidden").extend(self.output.get("tm"))

        # custom parameters
        self.pb.setLabelText("Custom parameters")
        self.pb.setValue(40)
        self.custom_inputs()

        # solver implementation
        self.pb.setLabelText("Building {0}Solver".format(self.classname))
        self.pb.setValue(60)
        self.custom_build()

        # connect
        self.pb.setLabelText("Connecting")
        self.pb.setValue(80)
        self.connect()

        # style
        self.pb.setLabelText("Styling")
        self.pb.setValue(100)
        self.style()
        self.pb.close()

        # refresh softimage ui
        si.Refresh()

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
        for x in self.helpers.get("hidden"):
            x.Properties("Visibility").Parameters("viewvis").Value = False
        # link anim visibility with solver state
        for anim in self.input.get("anim"):
            viewvis = anim.Properties("Visibility").Parameters("viewvis")
            viewvis.AddExpression(self.input.get("blendweight").FullName)

    @property
    def state(self):
        if self.input.get("active"):
            return self.input.get("active").Value
        return None

    @state.setter
    def state(self, value):
        if self.input.get("active"):
            self.input.get("active").Value = value
            self.input.get("blendweight").Value = float(value)

    def destroy(self):
        si.DeleteObj("B:{}".format(self.obj))

    @staticmethod
    def get_distance(src, dst):
        v = dst.Kinematics.Global.Transform.Translation
        v.SubInPlace(src.Kinematics.Global.Transform.Translation)
        return v.Length()

    @classmethod
    def new(cls, skeleton, name=None):
        # solver objs
        obj = si.ActiveSceneRoot.AddNull()
        s = cls(obj, name=name)
        s.output["root"] = obj.AddNull()
        s.helpers["root"] = obj.AddNull()
        s.input["root"] = obj.AddNull()
        # rename
        s.obj.Name = cls.nm.qn(s.solvername + "Solver", "group")
        s.output["root"].Name = cls.nm.qn(s.solvername + "Output", "group")
        s.helpers["root"].Name = cls.nm.qn(s.solvername + "Helpers", "group")
        s.input["root"].Name = cls.nm.qn(s.solvername + "Input", "group")
        # add to hidden list
        s.helpers.get("hidden").extend([s.obj, s.input.get("root"),
                                       s.output.get("root"),
                                       s.helpers.get("root")])
        # build
        s.build(skeleton)
        s.update()  # update mutable data serialization
        return s

    @classmethod
    def from_name(cls, name):
        name = cls.nm.qn(name + "Solver", "group")
        obj = siget(name)
        return cls(obj)
