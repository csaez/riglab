from wishlib.si import si


class Joint(object):

    @classmethod
    def new(cls, parent=None):
        parent = parent or si.ActiveSceneRoot
        n = parent.AddNull()
        n.Kinematics.Local.Transform = parent.Kinematics.Local.Transform
        j = cls(n)
        return j

    def __init__(self, null, **kwds):
        super(Joint, self).__init__()
        self.obj = null
        self.obj.Parameters("primary_icon").Value = 2
        self.obj.Parameters("shadow_icon").Value = 4
        self.obj.Parameters("shadow_scaleY").Value = 0.5
        self.obj.Parameters("shadow_scaleZ").Value = 0.25
        for k, v in kwds.iteritems():
            if hasattr(self, k):
                setattr(self, k, v)

    @property
    def size(self):
        return self.obj.Parameters("size").Value

    @size.setter
    def size(self, value):
        self.obj.Parameters("shadow_offsetX").Value = self.length / (2 * value)
        self.obj.Parameters("shadow_scaleX").Value = self.length / value
        self.obj.Parameters("size").Value = value

    @property
    def length(self):
        return self.obj.Parameters("shadow_scaleX").Value * self.size

    @length.setter
    def length(self, value):
        self.obj.Parameters("shadow_scaleX").Value = value / self.size
        self.obj.Parameters("shadow_offsetX").Value = (value / self.size) / 2
