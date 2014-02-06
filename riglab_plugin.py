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

from wishlib.si import si, sisel, log, C, show_qt


def XSILoadPlugin(in_reg):
    in_reg.Name = "RigLab Plugin"
    in_reg.Author = "csaez"
    in_reg.Major = 1.0
    in_reg.Minor = 0.0
    in_reg.UserData = ""
    in_reg.RegisterCommand("QuickLab", "quicklab")
    in_reg.RegisterCommand("RigLab Editor", "riglab")
    in_reg.RegisterCommand("Curve To Nulls", "curve2null")
    in_reg.RegisterCommand("Nulls To Curve", "null2curve")
    in_reg.RegisterCommand("Align Nulls To Curve", "align2curve")
    in_reg.RegisterCommand("Orthogonalize Selection", "orthogonalize")
    in_reg.RegisterCommand("Draw Linear Curve Into Mesh", "draw_linear_curve")
    in_reg.RegisterEvent("CloseScene", C.siOnCloseScene)
    return True


def XSIUnloadPlugin(in_reg):
    log("{} has been unloaded".format(in_reg.Name), C.siVerbose)
    return True


def QuickLab_Execute():
    log("QuickLab_Execute called", C.siVerbose)
    if sisel.Count != 1:
        return False
    from PyQt4.QtGui import QCursor
    from riglab.layout.quicklab import QuickLab
    pos = QCursor.pos()
    show_qt(QuickLab, modal=True,
            onshow_event=lambda x: x.move(pos.x(), pos.y()))
    return True


def RigLabEditor_Execute():
    log("RigLabEditor_Execute called", C.siVerbose)
    from riglab.layout.editor import Editor
    show_qt(Editor)
    return True


def CurveToNulls_Execute():
    log("CurvetoNulls_Execute called", C.siVerbose)
    from riglab.utils import curve2null
    si.SelectObj([n for c in list(sisel) for n in curve2null(c)])
    return True


def NullsToCurve_Execute():
    log("NullsToCurve_Execute called", C.siVerbose)
    from riglab.utils import sel2curve
    si.SelectObj(sel2curve(list(sisel)))
    return True


def AlignNullsToCurve_Execute():
    log("AlignNullsToCurve_Execute called", C.siVerbose)
    from riglab.utils import align2curve
    curve = si.PickObject()("PickedElement")
    if curve:
        align2curve(sisel, curve)
    return True


def DrawLinearCurveIntoMesh_Execute():
    log("DrawLinearCurveIntoMesh_Execute called", C.siVerbose)
    from riglab.utils import draw_linear_curve
    draw_linear_curve(sisel)
    return True


def OrthogonalizeSelection_Execute():
    log("OrthogonalizeSelection_Execute called", C.siVerbose)
    from riglab.utils import orthogonalize, deep
    for obj in sorted(list(sisel), key=deep):
        orthogonalize(obj)
    return True


def CloseScene_OnEvent(in_ctxt):
    log("CloseScene_OnEvent called", C.siVerbose)
    import sys
    module = "riglab"
    if len(module):
        for k in sys.modules.keys():
            if k.startswith(module):
                del sys.modules[k]
    return True
