from wishlib.si import si, siget, C, SIWrapper, sianchor
from wishlib.qt.QtGui import QProgressDialog

from .. import naming
from .. import bonetools
from ..manipulator import Manipulator


class Base(SIWrapper):
    # naming manager
    nm = naming.Manager()
    nm.rule = "3dobject"
    # progress bar
    pb = QProgressDialog(sianchor())
    pb.setMinimum(0)
    pb.setMaximum(100)

    def __init__(self, obj, name=None):
        self.classname = self.__class__.__name__
        self.solvername = name or self.classname
        self.input = {"root": None,
                      "parameters": None,
                      "active": None,
                      "blendweight": None,
                      "skeleton": list(),
                      "anim": list()}
        self.output = {"root": None,
                       "tm": list()}
        self.helper = {"root": None,
                       "hidden": list(),
                       "curve": None}
        super(Base, self).__init__(obj, "Solver_Data")

    def build(self, skeleton):
        if not self.validate(skeleton):
            return
        self.input["skeleton"] = list(skeleton)

        # init
        self.pb.setLabelText("Init solver")
        self.pb.setValue(10)
        self.pb.show()
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
        self.pb.setLabelText("Setting input parameters")
        self.pb.setValue(20)
        self.custom_inputs()

        # anim controls
        self.pb.setLabelText("Setting anim controls")
        self.pb.setValue(30)
        self.create_anim()

        # solver implementation
        self.pb.setLabelText("Building {0}Solver".format(self.classname))
        self.pb.setValue(50)
        self.custom_build()

        # connect
        self.pb.setLabelText("Connecting")
        self.pb.setValue(70)
        first = bonetools.deep(self.input["skeleton"][0])
        next = bonetools.deep(self.input["skeleton"][1])
        if first <= next:
            self.connect()
        else:
            self.connect_reverse()

        # style
        self.pb.setLabelText("Styling")
        self.pb.setValue(90)
        self.style()

        # refresh softimage ui
        self.pb.setLabelText("Serializing")
        self.pb.setValue(100)
        self.update()
        si.Refresh()

        self.pb.close()

    def create_anim(self):
        self.helper["curve"] = bonetools.sel2curve(self.input.get("skeleton"),
                                                   parent=self.helper["root"])
        self.helper["curve"].Name = self.nm.qn(self.solvername, "curve")
        self.helper["hidden"].append(self.helper.get("curve"))
        self.custom_anim()

    def connect(self, compensate=True):
        for i, bone in enumerate(self.input.get("skeleton")[:-1]):
            target = self.output.get("tm")[i]
            cns = bone.Kinematics.AddConstraint("Pose", target, compensate)
            for param in ("active", "blendweight"):
                expr = self.input.get(param).FullName
                cns.Parameters(param).AddExpression(expr)

    def connect_reverse(self, compensate=True):
        for i, bone in enumerate(self.input.get("skeleton")[1:]):
            target = self.output.get("tm")[i]
            cns = bone.Kinematics.AddConstraint("Pose", target, compensate)
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
        raise NotImplementedError()

    @state.setter
    def state(self, value):
        if self.input.get("active"):
            self.input.get("active").Value = value
            self.input.get("blendweight").Value = float(value)

    def destroy(self):
        si.DeleteObj("B:{}".format(self.obj))

    def snap(self):
        state = self.state
        self.state = False
        try:
            for anim in self.input.get("anim"):
                Manipulator(anim).snap()
        except:
            raise  # raise with no arguments re-raise the last exception
        finally:
            self.state = state

    @classmethod
    def new(cls, skeleton, name=None):
        if not cls.validate(skeleton):
            return
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

    @staticmethod
    def validate(skeleton):
        return True

    def custom_anim(self):
        pass

    def custom_build(self):
        pass
