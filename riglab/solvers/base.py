# This file is part of riglab.
# Copyright (C) 2014  Cesar Saez

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

import naming
from wishlib.si import si, siget, C, SIWrapper
from wishlib.utils import JSONDict

from .. import cache
from .. import utils
from ..manipulator import Manipulator


class Base(SIWrapper):
    # naming manager
    nm = naming.Manager()
    nm.rule = "3dobject"
    shape_color = JSONDict(
        os.path.join(os.path.expanduser("~"), "riglab", "shape_color.json"))

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
        self._mute = True
        super(Base, self).__init__(obj, "Solver_Data")
        self._mute = False

    def build(self, skeleton):
        if not self.validate(skeleton):
            return
        self.input["skeleton"] = list(skeleton)

        # init
        limit = len(self.input.get("skeleton"))
        if limit > 1:
            limit -= 1
        for i, bone in enumerate(self.input.get("skeleton")):
            # set bone params
            for param in ("cnsscl", "pivotactive", "pivotcompactive"):
                bone.Kinematics.Local.Parameters(param).Value = False
            if i < limit:
                # set outputs
                name = self.nm.qn(self.name, i, "rig", side=self.side)
                self.output["tm"].append(self.output.get("root").AddNull(name))
        self.helper.get("hidden").extend(self.output.get("tm"))
        # custom parameters
        self.custom_inputs()
        # anim controls
        self.create_anim()
        # solver implementation
        self.custom_build()
        # connect
        if self.reversed():
            self.connect_reverse()
        else:
            self.connect()
        # style
        self.style()
        # refresh softimage ui
        self.update()
        # si.Refresh()

    def create_anim(self):
        if len(self.input.get("skeleton")) > 1:
            # create a curve from skeleton
            self.helper["curve"] = utils.sel2curve(
                self.input.get("skeleton"), parent=self.helper["root"])
            self.helper["curve"].Name = self.nm.qn(
                self.name, "curve", side=self.side)
            self.helper["hidden"].append(self.helper.get("curve"))
        self.custom_anim()

    def connect(self, compensate=True):
        skeleton = self.input.get("skeleton")
        if len(skeleton) > 1:
            skeleton = skeleton[:-1]
        for i, bone in enumerate(skeleton):
            target = self.output.get("tm")[i]
            cns = bone.Kinematics.AddConstraint("Pose", target, compensate)
            for param in ("active", "blendweight"):
                expr = self.input.get(param).FullName
                cns.Parameters(param).AddExpression(expr)

    def connect_reverse(self, compensate=True):
        skeleton = self.input.get("skeleton")
        if len(skeleton) > 1:
            skeleton = skeleton[1:]
        for i, bone in enumerate(skeleton):
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

    def get_manipulator(self, name):
        if not hasattr(cache, "manip"):
            cache.manip = dict()
        m = cache.manip.get(name)
        if not m:
            m = Manipulator(siget(name))
            cache.manip[name] = m
        return m

    @property
    def state(self):
        if self.input.get("active"):
            return bool(self.input.get("blendweight").Value)
        raise NotImplementedError()

    @state.setter
    def state(self, value):
        if self._mute:
            return
        if self.input.get("active"):
            self.input.get("blendweight").Value = float(value)
            self.input.get("active").Value = value

    def destroy(self):
        for x in self.input.get("anim"):
            del cache.manip[x.FullName]
        si.DeleteObj("B:{}".format(self.obj))

    def snap(self):
        state = self.state
        if state:
            self.state = False
        for anim in self.input.get("anim"):
            try:
                self.get_manipulator(anim.FullName).snap()
            except Exception, err:
                print "ERROR:", err  # re-raise the last exception
        self.state = state

    @classmethod
    def new(cls, skeleton, name=None, root=None, side="C"):
        if not cls.validate(skeleton):
            return
        root = root or si.ActiveSceneRoot
        name = name or cls.__name__
        # solver objs
        obj = root.AddNull()
        s = cls(obj)
        s.side = side
        s.name = name
        s.output["root"] = obj.AddNull()
        s.helper["root"] = obj.AddNull()
        s.input["root"] = obj.AddNull()
        # rename
        cls.nm.rule = "3dobject"
        s.obj.Name = cls.nm.qn(s.name + "Root", "group", side=side)
        s.output["root"].Name = cls.nm.qn(
            s.name + "Output", "group", side=side)
        s.helper["root"].Name = cls.nm.qn(
            s.name + "Helper", "group", side=side)
        s.input["root"].Name = cls.nm.qn(s.name + "Input", "group", side=side)
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

    def reversed(self):
        if len(self.input["skeleton"]) == 1:
            return False
        first = utils.deep(self.input["skeleton"][0])
        last = [utils.deep(x) for x in self.input["skeleton"][1:]]
        if first <= sum(last) / len(last):
            return False
        return True

    @property
    def id(self):
        return self.name + "_" + self.side

    @id.setter
    def id(self, value):
        if self._mute:
            return
        splited = value.split("_")
        if len(splited) == 2:
            self.name = splited[0]
            self.side = splited[1]
