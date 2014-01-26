from wishlib.si import log, C, show_qt


def XSILoadPlugin(in_reg):
    in_reg.Name = "riglab_plugin"
    in_reg.Author = "csaez"
    in_reg.Major = 1.0
    in_reg.Minor = 0.0
    in_reg.UserData = ""
    in_reg.RegisterCommand("riglab", "riglab")
    return True


def XSIUnloadPlugin(in_reg):
    log("{} has been unloaded".format(in_reg.Name), C.siVerbose)
    return True


def riglab_Execute():
    log("riglabLibrary_Execute called", C.siVerbose)
    from riglab.layout.manager import Manager
    show_qt(Manager)
    return True
