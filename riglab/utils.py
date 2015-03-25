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

from collections import namedtuple
from pymel import core as pm
import naming


# HELPERS
def curve_data(curve):
    WORLD = [pm.dt.Vector(*x) for x in ((1, 0, 0), (0, 1, 0), (0, 0, 1),
                                        (-1, 0, 0), (0, -1, 0), (0, 0, -1))]
    matrices = list()
    length = list()
    pos = pm.PyNode(curve).getShape().getCVs()
    for i, p in enumerate(pos[:-1]):
        t = pos[i + 1] - p
        length.append(t.length())
        n = None
        if len(pos) > 2:
            bn = (lambda: pos[i + 2] - pos[i + 1],
                  lambda: pos[i - 1] - p)[int(i != 0)]()
            if not t.isParallel(bn):
                n = pm.dt.cross(t, bn)
        if n is None:
            min = 3.141592  # pi
            for w in WORLD:
                if 3.1415 / 4 - pm.dt.angle(t, w) < min:
                    n = w
            n = pm.dt.cross(t, n)
        bn = pm.dt.cross(n, t)
        xfo = pm.dt.Matrix(t.normal(), bn.normal(), n.normal())
        xfo.translate = p
        matrices.append(xfo)
    matrices.append(pm.dt.Matrix(matrices[-1]))
    matrices[-1].translate = pos[-1]
    length.append(0.0)
    return namedtuple("CurveData", "matrices, lengths")(matrices, length)


def rename_chain(chain, itemName, rule="3dobject"):
    nm = naming.Manager()
    nm.rule = rule
    for i, jnt in enumerate(chain):
        pm.rename(jnt, nm.qn(itemName, "jnt", i))


def align_matrix4(obj, matrix):
    obj = pm.PyNode(obj)
    obj.setMatrix(matrix, worldSpace=True)


def deep(obj, d=0):
    obj = pm.PyNode(obj)
    if not obj.getParent():
        return d
    return deep(obj.getParent(), d + 1)


def _get_coord(meshes=None):
    pass


def draw_linear_curve(meshes=None):
    pass


def align2curve(objs, curve):
    for i, (matrix, length) in enumerate(zip(*curve_data(curve))):
        try:
            obj = objs[i]
        except IndexError:
            return
        align_matrix4(obj, matrix)


def orthogonalize(obj):
    pass


# CONVERTERS
def sel2curve(sel, parent=None):
    pos = [x.getTranslation(space="world") for x in pm.selected()]
    curve = pm.curve(d=1, p=pos)
    if parent:
        curve.setParent(parent)
    return curve


def sel2chain(nulls):
    curve = sel2curve(nulls)
    root = curve2chain(curve)
    pm.delete(curve)
    return root


def curve2null(curve, parent=None):
    result = list()
    for i, (matrix, length) in enumerate(zip(*curve_data(curve))):
        result.append(pm.joint())
        align_matrix4(result[-1], matrix)
    pm.makeIdentity(result, apply=True, t=1, r=1, s=1, n=0, pn=1)
    result[0].setParent(parent)
    return result


def curve2chain(curve, parent=None):
    return curve2null(curve, parent)


def chain2null(chain, parent=None):
    pass
