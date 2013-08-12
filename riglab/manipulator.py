from wishlib.si import si, simath, SIWrapper
from rigicon.icon import Icon

from . import naming
from . import bonetools


class Manipulator(SIWrapper):
    nm = naming.Manager()

    def __init__(self, obj):
        self.spaces = dict()
        self.owner = {"obj": None, "class": None}
        self._snap_ref = {"obj": None,
                          "offset": (1, 0, 0, 0,
                                     0, 1, 0, 0,
                                     0, 0, 1, 0,
                                     0, 0, 0, 1)}
        super(Manipulator, self).__init__(obj, "Manipulator_Data")
        self.anim = obj
        self.icon = Icon(self.anim)
        self.zero = self.anim.Parent
        self.space = self.zero.Parent

    @classmethod
    def new(cls, parent=None):
        if parent is None:
            parent = si.ActiveSceneRoot
        space = parent.AddNull()
        zero = space.AddNull()
        icon = Icon.new()
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
        self.update()

    def destroy(self):
        for child in self.anim.Children:
            self.space.AddChild(child)
        for x in (self.anim, self.zero, self.space):
            si.DeleteObj(x)

    def align(self, dst, component="zero"):
        if hasattr(self, component):
            src = getattr(self, component)
            src.Kinematics.Global.Transform = dst.Kinematics.Global.Transform

    def neutral_pose(self):
        self.zero.Kinematics.Global.Transform = self.anim.Kinematics.Global.Transform

    def duplicate(self, number=1):
        results = list()
        copies = si.Duplicate((self.space, self.zero, self.anim), number)
        for i in range(number):
            i *= 3
            self.space.Parent.AddChild(copies[i + 0])
            copies[i + 0].AddChild(copies[i + 1])
            copies[i + 1].AddChild(copies[i + 2])
            results.append(self.__class__(copies[i + 2]))
        return results

    @property
    def parent(self):
        return self.space.Parent

    @parent.setter
    def parent(self, obj):
        if obj:
            obj.AddChild(self.space)
            self.update()

    def snap_ref(self, ref):
        m4 = self.zero.Kinematics.Global.Transform.Matrix4
        refM4 = ref.Kinematics.Global.Transform.Matrix4
        refM4.InvertInPlace()
        m4.MulInPlace(refM4)
        self._snap_ref = {"obj": ref, "offset": m4.Get2()}

    def snap(self):
        obj = self._snap_ref.get("obj")
        if obj is not None:
            m4 = simath.CreateMatrix4(*self._snap_ref["offset"])
            m4.MulInPlace(obj.Kinematics.Global.Transform.Matrix4)
            bonetools.align_matrix4(self.anim, m4)
