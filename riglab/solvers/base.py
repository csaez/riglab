from wishlib.si import si, siget, C, SIWrapper, sianchor
from wishlib.qt.QtGui import QProgressDialog

from .. import naming
from .. import bonetools


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
        self.helper = {"root": None,
                       "hidden": list(),
                       "curve": None}
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
        self.helper.get("hidden").extend(self.output.get("tm"))

        # custom parameters
        self.pb.setLabelText("Custom parameters")
        self.pb.setValue(40)
        self.custom_inputs()

        # anim controls
        self.pb.setLabelText("Creating anim controls")
        self.pb.setValue(60)
        self.create_anim()

        # solver implementation
        self.pb.setLabelText("Building {0}Solver".format(self.classname))
        self.pb.setValue(80)
        self.custom_build()

        # connect
        self.pb.setLabelText("Connecting")
        self.pb.setValue(90)
        a = bonetools.get_deep(self.input["skeleton"][0])
        b = bonetools.get_deep(self.input["skeleton"][-1])
        (self.connect, self.connect_reverse)[int(a > b)]()

        # style
        self.pb.setLabelText("Styling")
        self.pb.setValue(100)
        self.style()
        self.pb.close()

        # refresh softimage ui
        self.update()
        si.Refresh()

    def create_anim(self):
        self.helper["curve"] = bonetools.sel2curve(self.input.get("skeleton"),
                                                   parent=self.helper["root"])
        self.helper["curve"].Name = self.nm.qn(self.solvername, "curve")
        self.helper["hidden"].append(self.helper.get("curve"))
        self.custom_anim()

    def custom_anim(self):
        # raise NotImplementedError()
        pass

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
            cns = bone.Kinematics.AddConstraint("Pose", target, True)
            for param in ("active", "blendweight"):
                expr = self.input.get(param).FullName
                cns.Parameters(param).AddExpression(expr)

    def connect_reverse(self):
        for i, bone in enumerate(self.input.get("skeleton")[1:]):
            target = self.output.get("tm")[i]
            cns = bone.Kinematics.AddConstraint("Pose", target, True)
            for param in ("active", "blendweight"):
                expr = self.input.get(param).FullName
                cns.Parameters(param).AddExpression(expr)

    def style(self):
        for x in self.helper.get("hidden"):
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

    @classmethod
    def new(cls, skeleton, name=None):
        # solver objs
        obj = si.ActiveSceneRoot.AddNull()
        s = cls(obj, name=name)
        s.output["root"] = obj.AddNull()
        s.helper["root"] = obj.AddNull()
        s.input["root"] = obj.AddNull()
        # rename
        s.obj.Name = cls.nm.qn(s.solvername + "Solver", "group")
        s.output["root"].Name = cls.nm.qn(s.solvername + "Output", "group")
        s.helper["root"].Name = cls.nm.qn(s.solvername + "Helper", "group")
        s.input["root"].Name = cls.nm.qn(s.solvername + "Input", "group")
        # add to hidden list
        s.helper.get("hidden").extend([s.obj, s.input.get("root"),
                                       s.output.get("root"),
                                       s.helper.get("root")])
        # build
        s.build(skeleton)
        s.update()  # update mutable data serialization
        return s

    @classmethod
    def from_name(cls, name):
        name = cls.nm.qn(name + "Solver", "group")
        obj = siget(name)
        return cls(obj)
