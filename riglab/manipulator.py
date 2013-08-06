from wishlib.si import si, SIWrapper
from rigicon.icon import Icon

from . import naming


class Manipulator(SIWrapper):
    nm = naming.Manager()

    def __init__(self, obj):
        self.spaces = dict()
        super(Manipulator, self).__init__(obj, "Manipulator_Data")
        self.anim = obj
        self.icon = Icon(self.anim)
        self.zero = self.anim.Parent
        self.space = self.zero.Parent

    @classmethod
    def create(cls, parent=None):
        if parent is None:
            parent = si.ActiveSceneRoot
        space = parent.AddNull()
        zero = space.AddNull()
        icon = Icon.create()
        anim = icon.obj
        zero.AddChild(anim)
        manipulator = cls(anim)
        return manipulator

    def add_space(self, name=None, target=None):
        if not name or target:
            return
        name = name or target.Name
        tm = self.zero.Kinematics.Global.Transform
        cns = self.space.Kinematics.AddConstraint("Pose", target, True)
        self.spaces[name] = cns
        self.zero.Kinematics.Global.Transform = tm
        self.space_switch(name)

    def remove_space(self, name):
        cns = self.spaces.get(name)
        if cns is not None and name != self.active_space:
            si.DeleteObj(cns)
            del self.spaces[name]

    @property
    def active_space(self):
        for name, cns in self.spaces.iteritems():
            if cns.Parameters("active").Value:
                return name
        return "default"

    @active_space.setter
    def active_space(self, name):
        tm = self.zero.Kinematics.Global.Transform
        for k, cns in self.spaces.iteritems():
            if cns is not None:
                cns.Parameters("active").Value = name == k
        self.zero.Kinematics.Global.Transform = tm

    def rename(self, *args, **kwds):
        with self.nm.override(rule="3dobject"):
            self.space.Name = self.nm.qn("group", *args, **kwds)
            self.zero.Name = self.nm.qn("zero", *args, **kwds)
            self.anim.Name = self.nm.qn("anim", *args, **kwds)

    def destroy(self):
        for child in self.anim.Children:
            self.space.AddChild(child)
        for x in (self.anim, self.zero, self.space):
            si.DeleteObj(x)

    def align(self, dst):
        self.zero.Kinematics.Global.Transform = dst.Kinematics.Global.Transform

    def set_neutral(self):
        self.zero.Kinematics.Global.Transform = self.anim.Kinematics.Global.Transform

    def duplicate(self, number=1):
        results = list()
        spaces = si.Duplicate(self.space, number)
        zeroes = si.Duplicate(self.zero, number)
        anims = si.Duplicate(self.anim, number)
        for i in range(number):
            self.space.Parent.AddChild(spaces[i])
            spaces[i].AddChild(zeroes[i])
            zeroes[i].AddChild(anims[i])
            results.append(self.__class__(anims[i]))
        return results

    def set_parent(self, obj):
        obj.AddChild(self.space)
        self.update()
