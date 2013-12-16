from riglab import solvers
from wishlib.si import *


def create_ikfk(sel):
    sel = list(sel)
    for i, cls in enumerate((solvers.IK, solvers.FK)):
        s = cls.new(sel)
        s.state = bool(i)


def switch():
    s = [solvers.IK(siget("IKSolver_000_C_GRP")),
         solvers.FK(siget("FKSolver_000_C_GRP"))]
    state = [x.state for x in s]
    for x in s:
        x.state = False
    for x in s:
        x.snap()
    for i, x in enumerate(s):
        x.state = not state[i]

# create_ikfk(sisel)
switch()


from wishlib.si import *


def match_center(src, tgt):
    tgt_pos = tgt.Kinematics.Global.Transform.Translation.Get2()
    src_pos = src.Kinematics.Global.Transform.Translation.Get2()
    offset = [src_pos[i] - tgt_pos[i] for i in range(3)]
    # match position
    tm = src.Kinematics.Global.Transform
    tm.SetTranslation(simath.CreateVector3(*tgt_pos))
    src.Kinematics.Global.Transform = tm
    # offset pointposition
    pnt_pos = list()
    for coord in zip(*src.ActivePrimitive.Geometry.Points.PositionArray):
        pnt_pos.append([coord[i] - offset[i] for i in range(3)])
    src.ActivePrimitive.Geometry.Points.PositionArray = zip(*pnt_pos)

match_center(sisel(0), sisel(1))
