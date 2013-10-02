RigLab
======
`riglab` is a rigging framework for Softimage.

Dependencies
------------
- [PyQtForSoftimage](#)
- [wishlib](#)
- [nose](#)
- [setuptools](#)

Installation
------------

- Get a xsiaddon file from [here](#) and drop it on a softimage viewport.

or...

- Install from the Python Package Index and copy `riglab_plugin.py` file
to a Softimage plugin directory.

    pip install riglab

Goals
-----
- **Prototyping**: there are plenty of awesome autorig scripts, but almost
all of them mix the skeleton creation with pre-established animation
behaviours. RigLab doesn't care about the skeletal structure (no guides) but
they behaviour. It works at a lower level than modular solutions but a lot
higher than constraints/solvers, making the prototyping process much easier
on a wide range of characters/props/environments.

- **Editing**: again, there's plenty of nice autorig scripts out there, but
most of them just manage the creation process and then dump the results
into the 3d scene leaving the editing side up to you. RigLab is not just
about creation, it's session persistent and gives you access to existing
rigs via the python API (this is also important for animation tools).

- **Reusability**: RigLab implements a layer serialization mechanism, you can
reuse any previous configuration without a single line of code (sort of
autorigs for free).

- **Pipeline friendly**: Riglab is highly customizable; names, shapes, solvers
and almost every component is selected from a customizable library, lots
of configuration files (JSON) with default values that make sense.

Ussage
------
Refer to the [documentation](#).
