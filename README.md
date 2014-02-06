RigLab
======
`riglab` is an open source (GPLv3) rigging framework for Softimage.

Dependencies
------------
- [PyQtForSoftimage](#)
- [wishlib](#)
- [rigicon](#)
- [naming](#)

Installation
------------
Get a xsiaddon file from [here](#) and drop it on a softimage viewport
(includes wishlib, rigicon and naming packages).

*or...*

Copy `riglab_plugin.py` to a Softimage plugin directory, clone the repo and
install the python modules typing in a terminal.

    python setup.py install

Goals
-----
`riglab` is in the making, but it is important set the goals of the project
early on in order to justify why I think we could do better than current
rigging conventions.

- **Deformation first**: A lot of auto-riggers out there use a guide system
to create the skeleton and animation rig at the same time, making really hard
iterate over the joint placement once the setup is created (rebuild tend to
be the only option). `riglab` encourages a different approach, where you
have to solve joint placement first, when everything is still clean and
simple, and then feed `riglab` with that skeleton in order to assign different
behaviors creating your animation rig.

- **Prototyping**: `riglab` works at a lower level than most modular auto-riggers,
but not as lower as vanilla DCCs, this allow solve a wide range of rigs using
behaviours as the generic building block, solving snaping between states
and multiple spaces "for free".

- **Editing**: most auto-rigger scripts manage the creation process and
dump the results into the 3d scene, leaving the editing side up to
you. `riglab` is not just about creation, it is session persistent and gives
you access to existing rigs via a rich python API or GUI tools (this is also
important for animation tools).

- **Reusability**: `riglab` implements a quite powerfull templating system,
this allows re-use any previous configuration without write a single
line of code.

- **Pipeline friendly**: `riglab` is highly customizable: names, shapes,
solvers and almost every component is selected from a library or defined by
text configuration files.

Ussage
------
Refer to the [documentation](#).
