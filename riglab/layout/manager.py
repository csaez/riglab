import os
import sys
from PyQt4 import QtCore, QtGui, uic
from wishlib.qt.QtGui import QMainWindow


class RigLab(object):

    def __init__(self):
        super(RigLab, self).__init__()
        self.scene_rigs = list()

    def add_rig(self, name):
        rig = Rig.new(name)
        self.scene_rigs.append(rig)
        return rig


class Rig(object):

    @classmethod
    def new(cls, name):
        return cls(name)

    def __init__(self, name):
        self.name = name
        self.mode = 0  # {0: deformation, 1: rigging}
        self.groups = {}
        self.add_group("default")

    def add_group(self, name):
        self.groups[name] = {"solvers": list(), "states": dict()}

    def add_solver(self, solver_type, group_name):
        if self.groups.get(group_name) is None:
            return
        s = Solver(solver_type, solver_type)
        self.groups[group_name]["solvers"].append(s)
        return s

    def save_state(self, group_name, name):
        grp = self.groups.get(group_name)
        if grp is None:
            return
        data = {}
        for s in grp["solvers"]:
            data[s.name] = s.state
        grp["states"][name] = data

    def apply_state(self, group_name, name):
        grp = self.groups.get(group_name)
        if not grp or not grp["states"].get(name):
            return
        for k, v in grp["states"][name].iteritems():
            solver = [x for x in grp["solvers"] if x.name == k][0]
            solver.state = v

    def remove_solver(self, solver):
        for k, v in self.groups.iteritems():
            if solver in v["solvers"]:
                v["solvers"] = [x for x in v["solvers"] if x != solver]
                for name, state in v["states"].iteritems():
                    del v["states"][name][solver.name]
                solver.destroy()


class Solver(object):

    def __init__(self, solver_name, solver_type):
        super(Solver, self).__init__()
        self.name = solver_name
        self.type = solver_type
        self.state = True

    def destroy(self):
        pass


class MyDelegate(QtGui.QItemDelegate):

    def sizeHint(self, option, index):
        return QtCore.QSize(32, 32)


class Manager(QMainWindow):

    MODES = ("Deformation", "Rigging")  # table matching Rig() indices
    IMAGES = {"check": "checkmark_icon&16.png",
              "group": "iconmonstr-folder-icon-256.png",
              "active_group": "iconmonstr-bookmark-14-icon-256.png",
              "ik": "iconmonstr-backarrow-59-icon-256.png",
              "fk": "iconmonstr-arrow-59-icon-256.png",
              "splineik": "iconmonstr-sound-wave-4-icon-256.png"}
    for k, v in IMAGES.iteritems():
        IMAGES[k] = os.path.join(os.path.dirname(__file__), "ui", "images", v)

    def __init__(self, parent=None):
        super(Manager, self).__init__(parent)
        self.riglab = RigLab()
        self._MUTE = False
        self._index = -1
        self.initUI()

    def initUI(self):
        ui_dir = os.path.join(os.path.dirname(__file__), "ui")
        self.ui = uic.loadUi(os.path.join(ui_dir, "manager.ui"), self)
        # resize stack via a delegate
        delegate = MyDelegate()
        self.ui.stack.setItemDelegate(delegate)
        # signals
        self.ui.stack.itemChanged.connect(self.stack_changed)
        self.ui.stack.setContextMenuPolicy(3)  # QtCore.Qt.CustomConextMenu
        self.connect(self.ui.stack,
                     QtCore.SIGNAL("customContextMenuRequested(QPoint)"),
                     self.stack_contextmenu)
        # rig signals
        self.ui.rigMenu.aboutToShow.connect(self.reload_rigmenu)
        self.ui.newRig.triggered.connect(self.newrig_clicked)
        for i, widget in enumerate((self.ui.deformationMode, self.ui.riggingMode)):
            QtCore.QObject.connect(
                widget, QtCore.SIGNAL("triggered()"),
                lambda v=i: setattr(self.active_rig, "mode", v))
        # group signals
        self.ui.addGroup.triggered.connect(self.addgroup_clicked)
        self.ui.defaultGroup.triggered.connect(self.defaultgroup_clicked)
        self.ui.addState.triggered.connect(self.savestate_clicked)
        # behaviour signals
        self.ui.addFK.triggered.connect(lambda: self.addsolver_clicked("fk"))
        self.ui.addIK.triggered.connect(lambda: self.addsolver_clicked("ik"))
        self.ui.addSplineIK.triggered.connect(
            lambda: self.addsolver_clicked("splineik"))
        self.ui.removeBehaviour.triggered.connect(self.removesolver_clicked)
        # set active rig
        self.active_rig = self.riglab.scene_rigs[
            0] if len(self.riglab.scene_rigs) else None

    # SLOTS
    def newrig_clicked(self):
        print self._MUTE
        if self._MUTE:
            return
        name, ok = QtGui.QInputDialog.getText(self, "New Rig", "Rig name:")
        if not ok:
            return
        self.active_rig = self.riglab.add_rig(str(name))

    def addgroup_clicked(self):
        if self._MUTE:
            return
        name, ok = QtGui.QInputDialog.getText(self, "Add Group", "Group name:")
        name = str(name)
        if not ok or not len(name):
            return
        self.active_rig.add_group(name)
        self.active_group = name

    def defaultgroup_clicked(self):
        if self._MUTE:
            return
        item = self.ui.stack.currentItem()
        if item:
            self.active_group = str(item.text(0))

    def savestate_clicked(self):
        if self._MUTE or not len(self.active_rig.groups[self.active_group]["solvers"]):
            return
        name, ok = QtGui.QInputDialog.getText(self, "Save state as...",
                                              "State name:")
        name = str(name)
        if not ok or not len(name):
            return
        self.active_rig.save_state(self.active_group, name)
        self.reload_stack()

    def state_changed(self, name, group_name):
        if self._MUTE:
            return
        self.active_rig.apply_state(group_name, name)
        self.reload_stack()

    def addsolver_clicked(self, solver):
        if self._MUTE:
            return
        self.active_rig.add_solver(solver, self.active_group)
        self.reload_stack()

    def removesolver_clicked(self, solver=None):
        item = self.ui.stack.currentItem()
        if self._MUTE or not item.parent():
            return
        solver_name = str(item.text(0))
        group_name = str(item.parent().text(0))
        solver = self.get_solver(solver_name, group_name)
        self.active_rig.remove_solver(solver)
        self.reload_stack()

    def stack_changed(self, item, column):
        if self._MUTE or item.childCount():
            return
        self.ui.stack.itemChanged.connect
        solver_name = str(item.text(0))
        solver = self.get_solver(solver_name, self.active_group)
        solver.state = bool(item.checkState(column))

    def stack_contextmenu(self, pos):
        item = self.ui.stack.itemAt(pos)
        menu = self.ui.groupMenu
        if not item or item.parent():
            menu = self.ui.behaviourMenu
        cursor = QtGui.QCursor.pos()
        menu.move(cursor.x(), cursor.y())
        menu.exec_()

    # UTILITY
    def reload_rigmenu(self):
        self._MUTE = True
        if not self.active_rig:
            self._MUTE = False
            return
        # add scene rigs
        action_names = [str(a.text()) for a in self.ui.activeRig.actions()]
        for i, rig in enumerate(self.riglab.scene_rigs):
            if rig.name not in action_names:
                action = self.ui.activeRig.addAction(rig.name)
                QtCore.QObject.connect(
                    action, QtCore.SIGNAL("triggered()"),
                    lambda v=rig: setattr(self, "active_rig", v))
        # set icons
        ICONS = (QtGui.QIcon(self.IMAGES.get("check")), QtGui.QIcon())
        for action in self.ui.activeRig.actions():
            index = int(str(action.text()) != self.active_rig.name)
            action.setIcon(ICONS[index])
        for action in self.ui.modeMenu.actions():
            index = int(str(action.text()) != self.MODES[self.active_rig.mode])
            action.setIcon(ICONS[index])
        self._MUTE = False

    def reload_stack(self):
        self._MUTE = True
        ICON = lambda x: QtGui.QIcon(self.IMAGES.get(x))
        # store view config
        config = [(self.ui.stack.topLevelItem(i).text(0),
                   self.ui.stack.topLevelItem(i).isExpanded(),
                   self.ui.stack.itemWidget(self.ui.stack.topLevelItem(i), 1).currentIndex())
                  for i in range(self.ui.stack.topLevelItemCount())]
        # redraw everything
        self.ui.stack.clear()
        for group_name, v in self.active_rig.groups.iteritems():
            # add groups
            group = QtGui.QTreeWidgetItem((group_name, ))
            index = int(group_name == self.active_group)
            group.setIcon(0, ICON(("group", "active_group")[index]))
            self.ui.stack.addTopLevelItem(group)
            # add state combobox
            state = QtGui.QComboBox()
            state.addItems(self.active_rig.groups[group_name]["states"].keys())
            QtCore.QObject.connect(
                state, QtCore.SIGNAL("currentIndexChanged(QString)"),
                lambda v, g=group_name: self.state_changed(str(v), g))
            self.ui.stack.setItemWidget(group, 1, state)
            # add solver
            for solver in v["solvers"]:
                s = QtGui.QTreeWidgetItem((solver.name, ""))
                s.setIcon(0, ICON(solver.type.lower()))
                group.addChild(s)
                s.setCheckState(1, 2 if solver.state else 0)
        # restore view config (by name)
        for i in range(self.ui.stack.topLevelItemCount()):
            item = self.ui.stack.topLevelItem(i)
            for value in config:
                if str(item.text(0)) != str(value[0]):
                    continue
                item.setExpanded(value[1])
                self.ui.stack.itemWidget(item, 1).setCurrentIndex(value[2])
        self._MUTE = False

    def disable_gui(self, value):
        widgets = (self.ui.stack, self.ui.groupMenu,
                   self.ui.behaviourMenu, self.ui.editSkeleton, self.ui.modeMenu)
        for w in widgets:
            w.setEnabled(value)

    def get_solver(self, solver_name, group_name):
        grp = self.active_rig.groups.get(group_name)
        if grp:
            s = [x for x in grp["solvers"] if x.name == solver_name]
            if len(s):
                return s[0]
        return None

    @property
    def active_rig(self):
        return self.riglab.scene_rigs[self._index] if self._index >= 0 else None

    @active_rig.setter
    def active_rig(self, rig):
        self.disable_gui(rig is not None)
        if rig is None:
            return
        self._index = self.riglab.scene_rigs.index(rig)
        self.reload_stack()

    @property
    def active_group(self):
        if self.active_rig:
            if hasattr(self.active_rig, "_active_group"):
                return self.active_rig._active_group
            return self.active_rig.groups.keys()[0]
        return None

    @active_group.setter
    def active_group(self, value):
        self.active_rig._active_group = value  # monkey patch the active group
        self.reload_stack()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Manager().show()
    sys.exit(app.exec_())
