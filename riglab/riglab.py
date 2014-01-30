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

import naming
from wishlib.si import si
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
