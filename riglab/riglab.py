from wishlib.si import si
from . import naming
from . import rig


class RigLab(object):
    nm = naming.Manager()

    def __init__(self):
        super(RigLab, self).__init__()
        # get rigs on scene
        self.scene_rigs = list()
        for x in si.ActiveSceneRoot.FindChildren2("*", "#model"):
            data = self.nm.decompose(x.Name, "model")
            if data and data.get("category") == "character":
                self.scene_rigs.append(rig.Rig(x))

    def add_rig(self, name):
        self.scene_rigs.append(rig.Rig.new(name))
        return self.scene_rigs[-1]
