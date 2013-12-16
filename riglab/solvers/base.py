from wishlib.si import si, C, SIWrapper

from .. import naming
from .. import bonetools
from ..manipulator import Manipulator


class Base(SIWrapper):
    # naming manager
    nm = naming.Manager()
    nm.rule = "3dobject"

    def __init__(self, obj):
        self.classname = self.__class__.__name__
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
        limit = len(self.input.get("skeleton")) - 1
        for i, bone in enumerate(self.input.get("skeleton")):
            # set bone params
            for param in ("cnsscl", "pivotactive", "pivotcompactive"):
                bone.Kinematics.Local.Parameters(param).Value = False
            if i < limit:
                # set outputs
                name = self.nm.qn(self.name, i, "rig")
                self.output["tm"].append(self.output.get("root").AddNull(name))
        self.helper.get("hidden").extend(self.output.get("tm"))

        # custom parameters
        self.custom_inputs()

        # anim controls
        self.create_anim()

        # solver implementation
        self.custom_build()

        # connect
        first = bonetools.deep(self.input["skeleton"][0])
        next = bonetools.deep(self.input["skeleton"][1])
        if first <= next:
            self.connect()
        else:
            self.connect_reverse()

        # style
        self.style()

        # refresh softimage ui
        self.update()
        si.Refresh()

    def create_anim(self):
        self.helper["curve"] = bonetools.sel2curve(self.input.get("skeleton"),
                                                   parent=self.helper["root"])
        self.helper["curve"].Name = self.nm.qn(self.name, "curve")
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
    def new(cls, skeleton, name=None, root=None):
        if not cls.validate(skeleton):
            return
        root = root or si.ActiveSceneRoot
        name = name or cls.__name__
        # solver objs
        obj = root.AddNull()
        s = cls(obj)
        s.name = name
        s.output["root"] = obj.AddNull()
        s.helper["root"] = obj.AddNull()
        s.input["root"] = obj.AddNull()
        # rename
        cls.nm.rule = "3dobject"
        s.obj.Name = cls.nm.qn(s.name + "Root", "group")
        s.output["root"].Name = cls.nm.qn(s.name + "Output", "group")
        s.helper["root"].Name = cls.nm.qn(s.name + "Helper", "group")
        s.input["root"].Name = cls.nm.qn(s.name + "Input", "group")
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
