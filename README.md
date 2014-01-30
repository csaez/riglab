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

- Get a xsiaddon file from [here](#) and drop it on a softimage viewport
(includes wishlib, rigicon and naming modules).

or...

- Clone the repo, copy `riglab_plugin.py` to a Softimage plugin directory
and install the python modules typing in a terminal.

    python setup.py install

Goals
-----
RigLab is in the making, but I thought it could be important list the
project's goals in order to justify why I think we could do better
than current rigging conventions and invite developers/riggers to collaborate
with me.

- **Deformation first**: A lot of auto-rigs out there uses a guide system
to create a skeleton+animation system making really hard relocate the
articulation points once the setup is created. RigLab encourage a completally
different approach, it allow set different solvers/behaviours to an existing
skeleton (like adjustment layers in photoshop), so you can create and test
the skeleton before apply any animation system keeping things simple.

- **Prototyping**: RigLab works at a lower level than the typical modular
autorig, but not as lower as vanilla constraints, it allow grouping and
multiple behaviour in the same joints making prototyping much easier
on a wide range of characters/props/environments.

- **Editing**: again, there's plenty of nice autorig scripts out there, but
most of them just manage the creation process and then dump the results
into the 3d scene leaving the editing side up to you. RigLab is not just
about creation, it's session persistent and gives you access to existing
rigs via a python API (this is also important for animation tools).

- **Reusability**: RigLab implements serialization/templating mechanisms,
this way you can reuse any previous configuration without write a single
line of code (sort of autorigs for free).

- **Pipeline friendly**: Riglab is highly customizable; names, shapes, solvers
and almost every component is selected from a customizable library and
configuration files (JSON) with default values that make sense.

Ussage
------
Refer to the [documentation](#).
