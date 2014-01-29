import itertools
import collections

import naming
from wishlib.si import si, simath, siget, sisel, SIWrapper

from . import solvers
from . import utils


class Rig(SIWrapper):
    # naming manager
    nm = naming.Manager()

    @classmethod
    def new(cls, in_name):
        i = 0
        cls.nm.rule = "model"
        name = cls.nm.qn(itemName=in_name, itemNumber=i, category="character")
        while siget(name) is not None:
            i += 1
            name = cls.nm.qn(
                itemName=in_name, itemNumber=i, category="character")
        model = si.ActiveSceneRoot.AddModel(None, name)
        for p in ("rendvis", "viewvis"):
            model.Properties("Visibility").Parameters(p).Value = False
            model.Properties("Visibility").Parameters(p).Value = False
        rig = cls(model)
        cls.nm.rule = "3dobject"
        for x in ("skeleton", "solvers", "meshes"):
            grp = model.AddNull()
            grp.Name = cls.nm.qn(x, "group")
            for p in ("rendvis", "viewvis"):
                grp.Properties("Visibility").Parameters(p).Value = False
                grp.Properties("Visibility").Parameters(p).Value = False
            rig.holders[x] = grp
        rig.update()
        return rig

    def __init__(self, model):
        self._mode = 0
        self.holders = dict()
        self.groups = dict()
        self.poses = [{}, {}]  # {0: deformation, 1: rigging}
        self._skeleton = list()
        self._meshes = list()
        self.solvers = dict()
        super(Rig, self).__init__(model, "rig_data")
        self.name = self.obj.Name
        # solver's cache,
        # it's not serialized because of softimage indirect dependencies
        self.solvers_pool = dict()

    def add_group(self, name):
        self.groups[name] = {"solvers": list(),
                             "states": dict(),
                             "active": None}
        self.update()

    def remove_group(self, name):
        grp = self.groups.get(name)
        if not grp:
            return
        for solver_id in grp["solvers"]:
            self.get_solver(solver_id).destroy()
            del self.solvers[solver_id]
        del self.groups[name]
        self.update()

    def get_skeleton(self, group_name=None):
        # get rig's skeleton
        if not group_name:
            result = list()
            for gn in self.groups.keys():
                result.extend(self.get_skeleton(gn))
            return result
        # get by group
        if not self.groups.get(group_name):
            return []
        skel = self._collect_from_solvers(
            group_name, lambda x: x.input["skeleton"])
        skel = set([x.FullName for x in skel])  # remove duplicates
        return [siget(x) for x in skel]

    def get_anim(self, group_name=None):
        # get rig's anim
        if not group_name:
            result = list()
            for gn in self.groups.keys():
                result.extend(self.get_anim(gn))
            return result
        # get by group
        if not self.groups.get(group_name):
            return []
        anim = self._collect_from_solvers(
            group_name, lambda x: x.input["anim"])
        anim = set([x.FullName for x in anim])  # remove duplicates
        return [siget(x) for x in anim]

    def _collect_from_solvers(self, group_name, query_function):
        """Utility function used to collect solver data in a group"""
        data = list()
        for solver_id in self.groups[group_name]["solvers"]:
            solver = self.get_solver(solver_id)
            data.extend(query_function(solver))
        return data

    def add_solver(self, solver_type, group_name, name=None, side="C"):
        if self.groups.get(group_name) is None or not hasattr(solvers, solver_type) or not sisel.Count:
            return
        # save selection
        skeleton = list(sisel)
        # ensure rigging mode
        self.mode = 1
        # save stack state
        solver_stack = [self.get_solver(x) for x in self.solvers]
        old_state = list()
        for x in solver_stack:
            old_state.append(x.state)
            x.state = False
        self.apply_pose(1)
        # add solver
        # if solver_name is not provided use solver_type
        name = name or solver_type
        side = str(side)
        name = self.unique_name(name, side)
        solver_class = getattr(solvers, solver_type)
        solver = solver_class.new(
            skeleton, name, self.holders["solvers"], side=side)
        self.solvers[solver.id] = solver.obj  # save solver root
        # groups
        self.groups[group_name]["solvers"].append(solver.id)
        self.update()
        # restore stack states
        for i, x in enumerate(solver_stack):
            x.state = old_state[i]
        si.SelectObj(skeleton)  # restore selection
        return solver

    def remove_solver(self, solver_id):
        solver = self.get_solver(solver_id)
        del self.solvers[solver_id]
        for k, v in self.groups.iteritems():
            if solver_id in v["solvers"]:
                v["solvers"] = [x for x in v["solvers"] if x != solver_id]
                for name, state in v["states"].iteritems():
                    del v["states"][name][solver.id]
                solver.destroy()
        self.update()

    def get_solver(self, solver_id):
        # look for the solver in cache
        s = self.solvers_pool.get(solver_id)
        # if it's not there then reintantiate
        if s is None:  # not cached
            obj = self.solvers.get(solver_id)
            if obj:
                solver_class = SIWrapper(obj, "Solver_Data").classname
                s = getattr(solvers, solver_class)(obj)
                # add it to the pool
                self.solvers_pool[solver_id] = s
        return s

    def get_solvers(self, group_name=None):
        if group_name and self.groups.get(group_name):
            return [self.get_solver(x) for x in self.groups.get("leg_L").get("solvers")]
        return [self.get_solver(x) for x in self.solvers.keys()]

    def get_dependencies(self, solver):
        result = list()
        for a in solver.input.get("anim"):
            n = solver.get_manipulator(a.FullName).active_space
            if n == "default":
                continue
            m = solver.get_manipulator(n)
            if not m or not m.owner.get("obj"):
                continue
            n = m.owner.get("obj").Name.split("_")
            solver_id = n[0].replace("Root", "") + "_" + n[2]
            result.append(self.get_solver(solver_id))
        return result

    def save_state(self, group_name, name):
        grp = self.groups.get(group_name)
        if grp is None:
            return
        data = {}
        for solver_id in grp["solvers"]:
            solver = self.get_solver(solver_id)
            data[solver_id] = solver.state
        grp["states"][name] = data
        self.update()

    def apply_state(self, group_name, name, snap=False):
        grp = self.groups.get(group_name)
        if not grp or not grp["states"].get(name):
            return
        # get solvers
        solvers = [self.get_solver(solver_id)
                   for solver_id in grp["solvers"]]
        # save states
        old_state = list()
        for solver in solvers:
            old_state.append(solver.state)
        if snap:
            # sort dependencies
            l = list()
            deps = dict([(s.id, [x.id for x in self.get_dependencies(s)])
                         for s in solvers])
            for k, d in deps.iteritems():
                if len(d):
                    l.append(k)
                    l.extend(d)
                for solver_id in d:
                    l.extend(deps.get(solver_id))
            c = collections.Counter(l)
            for solver_id in sorted(deps.keys(), key=lambda x: c[x], reverse=True):
                solver = self.get_solver(solver_id)
                if not solver.state:
                    solver.snap()  # snap
        # apply new state
        for state_name, state_value in grp["states"][name].iteritems():
            solver = [x for x in solvers if x.id == state_name][0]
            solver.state = state_value
        grp["active"] = name
        self.update()
        # check autokey
        if si.GetValue("preferences.animation.autokey"):
            # manage keyframes
            current_frame = si.GetValue("PlayControl.Current")
            for i, solver_id in enumerate(grp["solvers"]):
                solver = self.get_solver(solver_id)
                param = (solver.input.get("active"),
                         solver.input.get("blendweight"))
                si.SaveKeyOnKeyable(solver.input.get("anim"))
                si.SaveKey(param, current_frame)
                si.SaveKey(param, current_frame - 1, old_state[i])

    def export_data(self, group_name):
        if not self.groups.get(group_name):
            return
        data = {"solvers": list(), "states": dict()}
        # serialize solver stack
        for i, s in enumerate(self.groups[group_name]["solvers"]):
            data["solvers"].append(s.data)
        # copy states
        data["states"] = self.groups[group_name]["states"].copy()
        return data

    def load_data(self, group_name, data):
        pass
        # self.add_group(group_name)
        # for d in data["solvers"]:
        #     self.groups[group_name]["solvers"].append(
        #         solver.Solver.from_data(d))
        # self.groups[group_name]["states"] = data["states"].copy()

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        # _snapshot stores the solver states in order to switch modes
        if not hasattr(self, "_snapshot"):
            self._snapshot = dict()
        # manage states
        for id in self.solvers:
            solver = self.get_solver(id)
            # take a snapshot and disable solver
            if value == 0 and value != self._mode:
                self._snapshot[id] = solver.state
                solver.state = False
            # restore state
            else:
                snapshot = self._snapshot.get(id)
                if snapshot:
                    solver.state = snapshot
        self._mode = value  # update internal var
        self.apply_pose(value)  # apply pose
        self.update()  # update siwrapper

    @property
    def skeleton(self):
        return self._skeleton

    @skeleton.setter
    def skeleton(self, value):
        self._skeleton = sorted(value, key=utils.deep)
        self.parent_to(self._skeleton, self.holders["skeleton"])
        self.update()

    @property
    def meshes(self):
        return self._meshes

    @meshes.setter
    def meshes(self, value):
        self._meshes = sorted(value, key=utils.deep)
        self.parent_to(self._meshes, self.holders["meshes"])
        self.update()

    @staticmethod
    def parent_to(in_list, in_parent):
        names = [x.Name for x in in_list]
        for x in in_list:
            if x.Parent.Name not in names:
                in_parent.AddChild(x)

    def save_pose(self, mode=None):
        if mode is None:
            mode = self._mode
        for x in self.skeleton:
            m4 = x.Kinematics.Global.Transform.Matrix4.Get2()
            self.poses[mode][x.Name] = m4
        self.update()

    def apply_pose(self, mode=None):
        if mode is None:
            mode = self._mode
        skeleton = self.skeleton
        if mode == 1:
            # dont change pose on disabled solvers
            s1 = set([sk.FullName for g in self.groups
                      for sk in self.get_skeleton(g)])
            s2 = set([x.FullName for x in self.skeleton])
            skeleton = [siget(x) for x in s2.difference(s1)]
        tm = simath.CreateTransform()
        for x in skeleton:
            m4 = self.poses[mode].get(x.Name)
            if not m4:
                continue
            tm.SetMatrix4(simath.CreateMatrix4(m4))
            x.Kinematics.Global.Transform = tm

    def unique_name(self, in_name, in_side, n=0):
        with self.nm.override(rule="3dobject"):
            temp_name = in_name + str(n).zfill(2)
            while self.obj.FindChildren2(self.nm.qn(temp_name + "Root", "group", side=in_side)).Count:
                n += 1
                temp_name = in_name + str(n).zfill(2)
        return temp_name

    def get_manipulator(self, name):
        for solver_name in self.solvers.keys():
            solver = self.get_solver(solver_name)
            for anim in solver.input.get("anim"):
                if name == anim.Name:
                    return solver.get_manipulator(anim.FullName)
