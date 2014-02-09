# Class Methods:

### r = Rig.new(name)
Creates a new rig

# Instance Methods:

### r.add_group(group_id)
Self explanatory.

### r.remove_group(group_id)
Self explanatory.

### r.get_skeleton(group_id=None)
Return a subset of the skeleton affected by the behaviours of `group_id`.
If `group_id` is not defined it returns the skeleton for the entire rig.

### r.get_anim(group_id=None)
Same as get_skeleton but with animation controls.

### r.add_solver(solver_type, group_id, skeleton=None, name=None, side="C", negate=False)
Adds a new behaviour to group_id of the type defined by solver_type (could be FK, IK or SplineIK).

### r.get_solver(solver_id)
Returns a behaviour for a given id (uniquename_side).

### r.get_solvers(group_id=None)
Returns a list of the behaviours of a given group.

### r.save_state(group_id, name)
Saves the current state of the behaviour stack.

### r.apply_state(group_id, name, snap=False)
Self explanaroty.

### r.get_template(group_id)
Returns a dictionary with the definition (aka template) of the group.

### r.apply_template(group_id, template, invert=False, icon=True, negate=False)
Apply a template to a given group, the templte dict has to be solved before applying
it to a new group (relationship between skeleton).

### r.save_pose(mode=None)
Save the pose to the given mode, if None is passed it uses the current mode.

### r.apply_pose(mode=None)
Self explanatory

### r.get_manipulator(name)
Get a manipulator instance for a given obj fullname.

# Instance attributes:

### r.mode
Get and set the mode for the rig, where 0=binding and 1=animation.

### r.skeleton
Get and set the entire skeleton of the rig.

### r.meshes
Get and set the meshes of the rig.

