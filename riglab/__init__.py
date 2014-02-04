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
from . import cache


def add_rig(name):
    r = Rig.new(name)
    cache.rig[r.obj.FullName] = r
    return r


def list_rigs():
    nm = naming.Manager()
    result = list()
    for x in si.ActiveSceneRoot.FindChildren2("*", "#model"):
        data = nm.decompose(x.Name, "model")
        if data and data.get("category") == "character":
            result.append(x.Name)
    return result


def get_rig(name):
    # init cache
    if not hasattr(cache, "rig"):
        cache.rig = dict()
    # get obj and init rig
    o = siget(name)
    if not o:
        return None
    r = cache.rig.get(name)
    if not r:
        r = Rig(o)
        cache.rig[name] = r
    return r

scene_rigs = (get_rig(x) for x in list_rigs())
