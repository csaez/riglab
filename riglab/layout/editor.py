import os
import webbrowser

import naming
from PyQt4 import QtCore, QtGui, uic
from wishlib.qt.QtGui import QMainWindow
from wishlib.si import si, sisel, show_qt
from rigicon.layout.library_gui import RigIconLibrary

from .. import riglab
from .rename import Rename
from .shape_color import ShapeColor


class MyDelegate(QtGui.QItemDelegate):

    def sizeHint(self, option, index):
        return QtCore.QSize(32, 32)


class Editor(QMainWindow):

    MODES = ("Binding", "Animation")  # table matching Rig() indices
    IMAGES = {"check": "iconmonstr-check-mark-icon-256.png",
              "group": "iconmonstr-folder-icon-256.png",
              "ik": "iconmonstr-backarrow-59-icon-256.png",
              "fk": "iconmonstr-arrow-59-icon-256.png",
              "splineik": "iconmonstr-sound-wave-4-icon-256.png"}
    for k, v in IMAGES.iteritems():
        IMAGES[k] = os.path.join(os.path.dirname(__file__), "ui", "images", v)

    def __init__(self, parent=None):
        super(Editor, self).__init__(parent)
        self.riglab = riglab.RigLab()
        self._clipboard = None
        self._mute = False
        self._index = -1
        self.initUI()

    def initUI(self):
        ui_dir = os.path.join(os.path.dirname(__file__), "ui")
        self.ui = uic.loadUi(os.path.join(ui_dir, "editor.ui"), self)
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
        self.ui.reload.triggered.connect(self.reload_stack)
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
        self.ui.groupSkeleton.triggered.connect(self.groupSkeleton_clicked)
        self.ui.groupManipulators.triggered.connect(
            self.groupManipulators_clicked)
        # behaviour signals
        self.ui.addFK.triggered.connect(lambda: self.addsolver_clicked("FK"))
        self.ui.addIK.triggered.connect(lambda: self.addsolver_clicked("IK"))
        self.ui.addSplineIK.triggered.connect(
            lambda: self.addsolver_clicked("SplineIK"))
        self.ui.removeBehaviour.triggered.connect(self.removesolver_clicked)
        self.ui.snap.triggered.connect(self.snapsolver_clicked)
        self.ui.inspect.triggered.connect(self.inspectsolver_clicked)
        self.ui.solverSkeleton.triggered.connect(self.solverSkeleton_clicked)
        self.ui.solverManipulators.triggered.connect(
            self.solverManipulators_clicked)
        # manipulator signals
        self.ui.addSpace.triggered.connect(self.addspace_clicked)
        self.ui.removeSpace.triggered.connect(self.removespace_clicked)
        self.ui.fromSelection.triggered.connect(self.fromselection_clicked)
        self.ui.manDebug.triggered.connect(self.mandebug_clicked)
        self.ui.manVisibility.triggered.connect(self.manvisibility_clicked)
        # extras signals
        self.ui.namingConvention.triggered.connect(
            lambda: show_qt(naming.Editor, force_style=True))
        self.ui.shapeColor.triggered.connect(lambda: show_qt(ShapeColor))
        self.ui.rigiconLibrary.triggered.connect(
            lambda: show_qt(RigIconLibrary))
        self.ui.docs.triggered.connect(
            lambda: webbrowser.open("https://github.com/csaez/riglab", new=2))
        # set active rig
        self.active_rig = self.riglab.scene_rigs[
            0] if len(self.riglab.scene_rigs) else None
        # set autosnap's default to True
        self.autosnap = False
        self.autosnap_clicked()  # update icon

    # SLOTS
    def renameitem_clicked(self, model_index):
        # enabled just for groups
        if not self.active_group:
            return
        item = self.ui.stack.currentItem()
        current_name = str(item.text(0))
        split_name = current_name.split("_")
        data = self.get_name(default_name=split_name[0],
                             default_side=split_name[1])
        if not data or not len(data.name):
            return
        # define new group name
        new_name = data.name + "_" + data.side
        if current_name == new_name:
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
                if not v.get(s.id):
                    continue
                v[new_name] = v[s.id]
            # rename
            s.name = new_name
        self.reload_stack()

    def newrig_clicked(self):
        name, ok = QtGui.QInputDialog.getText(self, "New Rig", "Rig name:")
        if not ok:
            return
        self.active_rig = self.riglab.add_rig(str(name))

    def mode_changed(self, index):
        if self._mute or not self.active_rig:
            return
        self.active_rig.mode = index

    def setSkeleton_clicked(self):
        self.active_rig.skeleton = sisel
        for i in range(2):
            self.active_rig.save_pose(i)

    def setMeshes_clicked(self):
        self.active_rig.meshes = sisel

    def copytemplate_clicked(self):
        self._clipboard = self.active_rig.export_data(self.active_group)

    def pastetemplate_clicked(self):
        if not self._clipboard:
            return
        self.active_rig.load_data(self.active_group, self._clipboard.copy())
        self.reload_stack()

    def addgroup_clicked(self):
        data = self.get_name()
        if not data or not len(data.name):
            return
        name = data.name + "_" + data.side
        # name, ok = QtGui.QInputDialog.getText(self, "Add Group", "Group name:")
        # name = str(name)
        # if not ok or not len(name):
        #     return
        self.active_rig.add_group(name)
        self.reload_stack()

    def removegroup_clicked(self):
        if self.active_group is None:
            return
        if len(self.active_rig.groups[self.active_group]["solvers"]):
            msgbox = QtGui.QMessageBox(self)
            msgbox.addButton(QtGui.QMessageBox.Yes)
            msgbox.addButton(QtGui.QMessageBox.No)
            msgbox.setText("The group isn't empty.\nDo you want to continue?")
            msgbox.setIcon(QtGui.QMessageBox.Question)
            if msgbox.exec_() == QtGui.QMessageBox.No:
                return
        self.active_rig.remove_group(self.active_group)
        self.reload_stack()

    def savestate_clicked(self):
        if self.active_group is None:
            return
        n, ok = QtGui.QInputDialog.getText(self, "Save state", "State name:")
        n = str(n)
        if not ok or not len(n):
            return
        self.active_rig.save_state(self.active_group, n)
        self.reload_stack()

    def removestate_clicked(self):
        if self.active_group is None:
            return
        states = self.active_rig.groups[self.active_group]["states"]
        if not len(states):
            return
        n, ok = QtGui.QInputDialog.getItem(
            self, "Remove State", "States:", states.keys(), 0, False)
        if not ok:
            return
        del self.active_rig.groups[self.active_group]["states"][str(n)]
        self.reload_stack()

    def autosnap_clicked(self):
        self.autosnap = not self.autosnap
        icon = (QtGui.QIcon(), QtGui.QIcon(self.IMAGES.get("check")))
        self.ui.autoSnap.setIcon(icon[int(self.autosnap)])

    def state_changed(self, name, group_name):
        if self._mute:
            return
        self.active_rig.apply_state(group_name, name, snap=self.autosnap)
        self.reload_stack()

    def groupSkeleton_clicked(self):
        if self.active_group is None:
            return
        si.SelectObj(self.active_rig.get_skeleton(self.active_group))

    def groupManipulators_clicked(self):
        if self.active_group is None:
            return
        si.SelectObj(self.active_rig.get_anim(self.active_group))

    def addsolver_clicked(self, solver_type):
        if self.active_group is None:
            return
        data = self.get_name(solver_type, self.active_group.split("_")[-1])
        if data and len(data.name):
            self.active_rig.add_solver(
                solver_type, self.active_group, name=data.name, side=data.side)
            self.reload_stack()

    def removesolver_clicked(self, solver=None):
        if not self.active_solver:
            return
        solver_name = str(self.ui.stack.currentItem().text(0))
        self.active_rig.remove_solver(solver_name)
        self.reload_stack()

    def snapsolver_clicked(self):
        if not self.active_solver:
            return
        solver_name = str(self.ui.stack.currentItem().text(0))
        self.active_rig.get_solver(solver_name).snap()

    def inspectsolver_clicked(self):
        if not self.active_solver:
            return
        solver_name = str(self.ui.stack.currentItem().text(0))
        p = self.active_rig.get_solver(solver_name).input.get("parameters")
        if p:
            si.InspectObj(p)

    def solverSkeleton_clicked(self):
        if not self.active_solver:
            return
        solver_name = str(self.ui.stack.currentItem().text(0))
        si.SelectObj(self.active_rig.get_solver(solver_name).input["skeleton"])

    def solverManipulators_clicked(self):
        if not self.active_solver:
            return
        solver_name = str(self.ui.stack.currentItem().text(0))
        si.SelectObj(self.active_rig.get_solver(solver_name).input["anim"])

    def addspace_clicked(self):
        if not self.active_manipulator:
            return
        m = self.active_rig.get_manipulator(self.active_manipulator)
        picked = si.PickObject()("PickedElement")
        if picked:
            m.add_space(name=picked.FullName, target=picked)
            m.active_space = picked.FullName
        self.reload_stack()

    def removespace_clicked(self):
        if not self.active_manipulator:
            return
        m = self.active_rig.get_manipulator(self.active_manipulator)
        # check for spaces
        if not any(m.spaces.values()):
            return
        n, ok = QtGui.QInputDialog.getItem(
            self, "Remove Space", "Spaces:", m.spaces.keys(), 0, False)
        if ok:
            m.remove_space(str(n))
            self.reload_stack()

    def fromselection_clicked(self):
        # check selection
        if not sisel.Count:
            return
        # loop through groups
        for g in xrange(self.ui.stack.topLevelItemCount()):
            grp_widget = self.ui.stack.topLevelItem(g)
            # loop through solvers
            for s in xrange(grp_widget.childCount()):
                solver_widget = grp_widget.child(s)
                # loop through manipulators
                for a in xrange(solver_widget.childCount()):
                    anim_widget = solver_widget.child(a)
                    if str(sisel(0).Name) == str(anim_widget.text(0)):
                        self.ui.stack.setCurrentItem(anim_widget)
                        return

    def mandebug_clicked(self):
        if not self.active_manipulator:
            return
        m = self.active_rig.get_manipulator(self.active_manipulator)
        m.debug = not m.debug

    def manvisibility_clicked(self):
        if not self.active_manipulator:
            return
        m = self.active_rig.get_manipulator(self.active_manipulator)
        m.visibility = not m.visibility

    def stack_changed(self, item, column):
        if self._mute:
            return
        if item.childCount() and item.parent():  # it's a solver
            solver = self.active_rig.get_solver(str(item.text(0)))
            solver.state = bool(item.checkState(column))

    def stack_contextmenu(self, pos):
        # filter context using selection
        # if click on nothing then show the entire thing,
        # otherwise show group or behaviour.
        item = self.ui.stack.itemAt(pos)
        if item is None:
            menu = self.ui.menubar.children()[-1]
        elif item.parent() and not item.childCount():  # it is a manipulator
            menu = self.ui.manipulatorMenu
        elif item.parent() and item.childCount():  # it is a behaviour
            menu = self.ui.behaviourMenu
        else:
            menu = self.ui.groupMenu
        # show menubar as context menu
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
            for solver_id in v["solvers"]:
                solver = self.active_rig.get_solver(solver_id)
                s = QtGui.QTreeWidgetItem((solver.id, ""))
                s.setIcon(0, ICON(solver.classname.lower()))
                group.addChild(s)
                s.setCheckState(1, 2 if solver.state else 0)
                # add manipulators
                for a in solver.input.get("anim"):
                    anim = QtGui.QTreeWidgetItem((a.Name, ""))
                    s.addChild(anim)
                    spaces = QtGui.QComboBox()
                    m = solver.get_manipulator(a.FullName)
                    spaces.addItems(m.spaces.keys())
                    try:
                        spaces.setCurrentIndex(
                            m.spaces.keys().index(m.active_space))
                    except:
                        pass
                    self.ui.stack.setItemWidget(anim, 1, spaces)
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
                   self.ui.setMeshes, self.ui.modeMenu,
                   self.ui.manipulatorMenu)
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
            if item.parent() is None:
                return str(item.text(0))
        return None

    @property
    def active_solver(self):
        item = self.ui.stack.currentItem()
        if self.active_rig and item:
            if item.parent() is not None and item.childCount():
                return str(item.text(0))
        return None

    @property
    def active_manipulator(self):
        item = self.ui.stack.currentItem()
        if self.active_rig and item:
            if item.parent() is not None and not item.childCount():
                return str(item.text(0))
        return None

    def get_name(self, default_name=None, default_side="C"):
        ok, data = Rename.get_data(
            parent=self, name=default_name, side=default_side)
        if ok:
            return data
        return None
