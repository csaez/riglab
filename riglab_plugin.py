from wishlib.si import si, sisel, log, C, show_qt


def XSILoadPlugin(in_reg):
    in_reg.Name = "RigLab Plugin"
    in_reg.Author = "csaez"
    in_reg.Major = 1.0
    in_reg.Minor = 0.0
    in_reg.UserData = ""
    in_reg.RegisterCommand("RigLab Editor", "riglab")
    in_reg.RegisterCommand("Curve To Nulls", "curve2null")
    in_reg.RegisterCommand("Nulls To Curve", "null2curve")
    in_reg.RegisterCommand("Align Nulls To Curve", "align2curve")
    in_reg.RegisterCommand("Orthogonalize Selection", "orthogonalize")
    in_reg.RegisterCommand("Draw Linear Curve Into Mesh", "draw_linear_curve")
    return True


def XSIUnloadPlugin(in_reg):
    log("{} has been unloaded".format(in_reg.Name), C.siVerbose)
    return True


def RigLabEditor_Execute():
    log("RigLabEditor_Execute called", C.siVerbose)
    from riglab.layout.editor import Editor
    show_qt(Editor)
    return True


def CurveToNulls_Execute():
    log("CurvetoNulls_Execute called", C.siVerbose)
    from riglab.utils import curve2null
    si.SelectObj(curve2null(sisel(0)))
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
