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
from wishlib.si import si, siget
from .rig import Rig


class RigLab(object):
    nm = naming.Manager()

    def __init__(self):
        super(RigLab, self).__init__()
        self.pool = dict()  # cache

    def add_rig(self, name):
        return Rig.new(name)

    def list_rigs(self):
        result = list()
        for x in si.ActiveSceneRoot.FindChildren2("*", "#model"):
            data = self.nm.decompose(x.Name, "model")
            if data and data.get("category") == "character":
                result.append(x.Name)
        return result

    def get_rig(self, name):
        o = siget(name)
        if not o:
            return None
        r = self.pool.get(name)  # cache
        if not r:
            r = Rig(o)
            self.pool[name] = r
        return r

    @property
    def scene_rigs(self):
        return (self.get_rig(x) for x in self.list_rigs())
