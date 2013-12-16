import os
import sys
import json
import webbrowser
from PyQt4 import QtCore, QtGui, uic
from wishlib.qt.QtGui import QMainWindow
from wishlib.si import si, sisel, show_qt
from .. import riglab
from .. import naming
from rigicon.layout.library_gui import RigIconLibrary


class MyDelegate(QtGui.QItemDelegate):

    def sizeHint(self, option, index):
        return QtCore.QSize(32, 32)


class Manager(QMainWindow):

    MODES = ("Deformation", "Rigging")  # table matching Rig() indices
    IMAGES = {"check": "iconmonstr-check-mark-icon-256.png",
              "group": "iconmonstr-folder-icon-256.png",
              "ik": "iconmonstr-backarrow-59-icon-256.png",
              "fk": "iconmonstr-arrow-59-icon-256.png",
              "splineik": "iconmonstr-sound-wave-4-icon-256.png"}
    for k, v in IMAGES.iteritems():
        IMAGES[k] = os.path.join(os.path.dirname(__file__), "ui", "images", v)

    def __init__(self, parent=None):
        super(Manager, self).__init__(parent)
        self.riglab = riglab.RigLab()
        self._clipboard = None
        self._mute = False
        self._index = -1
        self.autosnap = False
        self.initUI()
        self.autosnap_clicked()

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
        self.ui.stack.doubleClicked.connect(self.renameitem_clicked)
        # rig signals
        self.ui.rigMenu.aboutToShow.connect(self.reload_rigmenu)
        self.ui.newRig.triggered.connect(self.newrig_clicked)
        for i, widget in enumerate((self.ui.deformationMode, self.ui.riggingMode)):
            QtCore.QObject.connect(
                widget, QtCore.SIGNAL("triggered()"),
                lambda v=i: self.mode_changed(v))
        self.ui.savePose.triggered.connect(lambda: self.active_rig.save_pose())
        self.ui.setSkeleton.triggered.connect(self.setSkeleton_clicked)
        self.ui.setMeshes.triggered.connect(self.setMeshes_clicked)
        # group signals
        self.ui.copyTemplate.triggered.connect(self.copytemplate_clicked)
        self.ui.pasteTemplate.triggered.connect(self.pastetemplate_clicked)
        self.ui.addGroup.triggered.connect(self.addgroup_clicked)
        self.ui.removeGroup.triggered.connect(self.removegroup_clicked)
        self.ui.addState.triggered.connect(self.savestate_clicked)
        self.ui.removeState.triggered.connect(self.removestate_clicked)
        self.ui.autoSnap.triggered.connect(self.autosnap_clicked)
        # behaviour signals
        self.ui.addFK.triggered.connect(lambda: self.addsolver_clicked("FK"))
        self.ui.addIK.triggered.connect(lambda: self.addsolver_clicked("IK"))
        self.ui.addSplineIK.triggered.connect(
            lambda: self.addsolver_clicked("SplineIK"))
        self.ui.removeBehaviour.triggered.connect(self.removesolver_clicked)
        self.ui.snap.triggered.connect(self.snapsolver_clicked)
        self.ui.inspect.triggered.connect(self.inspectsolver_clicked)
        # extras signals
        self.ui.namingConvention.triggered.connect(
            lambda: show_qt(naming.editor.Editor))
        self.ui.rigiconLibrary.triggered.connect(
            lambda: show_qt(RigIconLibrary))
        self.ui.docs.triggered.connect(
            lambda: webbrowser.open("https://github.com/csaez/riglab", new=2))
        # set active rig
        self.active_rig = self.riglab.scene_rigs[
            0] if len(self.riglab.scene_rigs) else None

    # SLOTS
    def renameitem_clicked(self, model_index):
        item = self.ui.stack.currentItem()
        current_name = str(item.text(0))
        new_name, ok = QtGui.QInputDialog.getText(
            self, "Rename item", "", text=current_name)
        new_name = str(new_name)
        if not ok and not len(new_name):
            return
        if item.parent() is None:  # group
            self.active_rig.groups[
                new_name] = self.active_rig.groups[current_name]
            del self.active_rig.groups[current_name]
        else:  # solver
            grp_name = str(item.parent().text(0))
            s = self.active_rig.get_solver(current_name)
            # update states
            for k, v in self.active_rig.groups[grp_name]["states"].iteritems():
                if not v.get(s.name):
                    continue
                v[new_name] = v[s.name]
            # rename
            s.name = new_name
        self.reload_stack()

    def newrig_clicked(self):
        if self._mute:
            return
        name, ok = QtGui.QInputDialog.getText(self, "New Rig", "Rig name:")
        if not ok:
            return
        self.active_rig = self.riglab.add_rig(str(name))

    def mode_changed(self, index):
        if self._mute or not self.active_rig:
            return
        self.active_rig.mode = index

    def setSkeleton_clicked(self):
        if self._mute or not self.active_rig:
            return
        self.active_rig.skeleton = sisel
        for i in range(2):
            self.active_rig.save_pose(i)

    def setMeshes_clicked(self):
        if self._mute or not self.active_rig:
            return
        self.active_rig.meshes = sisel

    def copytemplate_clicked(self):
        if self._mute or not self.active_rig:
            return
        self._clipboard = self.active_rig.export_data(self.active_group)

    def pastetemplate_clicked(self):
        if self._mute or not self.active_rig or not self._clipboard:
            return
        self.active_rig.load_data(self.active_group, self._clipboard.copy())
        self.reload_stack()

    def addgroup_clicked(self):
        if self._mute:
            return
        name, ok = QtGui.QInputDialog.getText(self, "Add Group", "Group name:")
        name = str(name)
        if not ok or not len(name):
            return
        self.active_rig.add_group(name)
        self.reload_stack()

    def removegroup_clicked(self):
        item = self.ui.stack.currentItem()
        if self._mute or item is None or item.parent() is not None:
            return
        grp_name = str(item.text(0))
        if len(self.active_rig.groups[grp_name]["solvers"]):
            msgbox = QtGui.QMessageBox(self)
            msgbox.addButton(QtGui.QMessageBox.Yes)
            msgbox.addButton(QtGui.QMessageBox.No)
            msgbox.setText("The group isn't empty.\nDo you want to continue?")
            msgbox.setIcon(QtGui.QMessageBox.Question)
            if msgbox.exec_() == QtGui.QMessageBox.No:
                return
        self.active_rig.remove_group(grp_name)
        self.reload_stack()

    def savestate_clicked(self):
        if self._mute or not self.active_group or not len(self.active_rig.groups[self.active_group]["solvers"]):
            return
        name, ok = QtGui.QInputDialog.getText(
            self, "Save state as...", "State name:")
        name = str(name)
        if not ok or not len(name):
            return
        self.active_rig.save_state(self.active_group, name)
        self.reload_stack()

    def removestate_clicked(self):
        if self._mute or not self.active_rig or self.active_group is None:
            return
        states = self.active_rig.groups[self.active_group]["states"].keys()
        if not len(states):
            return
        name, ok = QtGui.QInputDialog.getItem(
            self, "Remove State", "States:", states, 0, False)
        if not ok:
            return
        del self.active_rig.groups[self.active_group]["states"][str(name)]
        self.reload_stack()

    def autosnap_clicked(self):
        self.autosnap = not self.autosnap
        icon = (QtGui.QIcon(), QtGui.QIcon(self.IMAGES.get("check")))
        self.ui.autoSnap.setIcon(icon[int(self.autosnap)])

    def state_changed(self, name, group_name):
        if self._mute:
            return
        if self.autosnap:
            solvers = [self.active_rig.get_solver(solver_name)
                       for solver_name in self.active_rig.groups[group_name]["solvers"]]
            for solver in solvers:
                if not solver.state:
                    solver.snap()
        self.active_rig.apply_state(group_name, name)
        self.reload_stack()

    def addsolver_clicked(self, solver):
        if self._mute and self.active_group:
            return
        self.active_rig.add_solver(solver, self.active_group)
        self.reload_stack()

    def removesolver_clicked(self, solver=None):
        item = self.ui.stack.currentItem()
        if self._mute or item is None or item.parent() is None:
            return
        solver_name = str(item.text(0))
        self.active_rig.remove_solver(solver_name)
        self.reload_stack()

    def snapsolver_clicked(self):
        item = self.ui.stack.currentItem()
        if self._mute or item is None or item.parent() is None:
            return
        solver_name = str(item.text(0))
        self.active_rig.get_solver(solver_name).snap()

    def inspectsolver_clicked(self):
        item = self.ui.stack.currentItem()
        if self._mute or item is None or item.parent() is None:
            return
        solver_name = str(item.text(0))
        param = self.active_rig.get_solver(solver_name).input.get("parameters")
        if param:
            si.InspectObj(param)

    def stack_changed(self, item, column):
        if self._mute or item.childCount():
            return
        self.ui.stack.itemChanged.connect
        solver_name = str(item.text(0))
        solver = self.active_rig.get_solver(solver_name)
        solver.state = bool(item.checkState(column))

    def stack_contextmenu(self, pos):
        # show menubar as context menu
        menu = self.ui.menubar.children()[-1]
        cursor = QtGui.QCursor.pos()
        menu.move(cursor.x(), cursor.y())
        menu.exec_()

    # UTILITY
    def reload_rigmenu(self):
        self._mute = True
        if not self.active_rig:
            self._mute = False
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
        self._mute = False

    def reload_stack(self):
        self._mute = True
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
            # index = int(group_name == self.active_group)
            group.setIcon(0, ICON("group"))
            self.ui.stack.addTopLevelItem(group)
            # add state combobox
            states = self.active_rig.groups[group_name]["states"].keys()
            s = QtGui.QComboBox()
            s.addItems(states)
            QtCore.QObject.connect(
                s, QtCore.SIGNAL("currentIndexChanged(QString)"),
                lambda v, g=group_name: self.state_changed(str(v), g))
            self.ui.stack.setItemWidget(group, 1, s)
            active_state = self.active_rig.groups[group_name].get("active")
            if active_state:
                try:
                    s.setCurrentIndex(states.index(active_state))
                except ValueError:
                    pass
            # add solver
            for solver_name in v["solvers"]:
                solver = self.active_rig.get_solver(solver_name)
                s = QtGui.QTreeWidgetItem((solver.name, ""))
                s.setIcon(0, ICON(solver.classname.lower()))
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
        self._mute = False

    def disable_gui(self, value):
        widgets = (self.ui.stack, self.ui.groupMenu,
                   self.ui.behaviourMenu, self.ui.setSkeleton,
                   self.ui.setMeshes, self.ui.modeMenu)
        for w in widgets:
            w.setEnabled(value)

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
        item = self.ui.stack.currentItem()
        if self.active_rig and item:
            if item.parent() is not None:
                item = item.parent()
            return str(item.text(0))
        return None


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Manager().show()
    sys.exit(app.exec_())
