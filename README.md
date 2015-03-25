RigLab
======

`riglab` is an open source (GPLv3) rigging framework with an strong focus on
usability and API.

Wait... rigging framework?

Yes! I wrote [an article](#) on why a framework instead of an auto-rigger
system, the main differences are: serialization through extensive use of
metadata, strong API and extensability (check the *project goals* for a
high-level description).

The project was firstly designed to be ran within Softimage, that's why all
previous videos and articles are Softimage based, but after Autodesk announced
Softimage's EOL I started to work on a Maya port that quickly become an entire
re-write.

There's no ETA yet, but I'm working hard on it and there should be a new
preview video showing `riglab` running on Maya soon (and maybe an early alpha
release, we will see).

I'm absolutely sure that there are valuable ideas behind the project and the
Softimage version already shown some of these ideas in action (check the
preview videos!), this project is not meant to be your average modular rigging
system.


## Previews/Demos

- [Album](http://www.vimeo.com/album/2631181) on Vimeo.
- [Articles](http://www.cesarsaez.me/tag/riglab.html) about it on my website.


## Project Goals

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


## Dependencies

`riglab` relies on the following libraries:

- [PySide](#) (included in Maya>=2014)
- [nosetest](#) (testing)
- [mock](#) (testing)
- [coverage](#) (testing)

Good news is you don need to worry about any of these unless you want to run the test suite or contribute code to the project (untested pull requests will not be accepted... time to step up!).


## Installation

There are several ways to get `riglab` installed on your system.
- You can install it as a standard python library through its `setup.py` script.
- You can clone the repo and add the inner `riglab` directory to your `PYTHONPATH` environment variable.
- You can copy/symlink the inner `riglab` directory to your `~/maya/scripts` directory.

##### There are so many options, what should I choose?

My humble recommendation:
- Users: copy the inner riglab dir to `~/maya/scripts`
- Developers: `setup.py` or `PYTHONPATH` (you probably know what suits you better).


## Contribute

It's too soon for pull requests, but if you want to help to shape the project please contact me through Github's issues,  email or any social media sites (I'm not hard to find).


## Ussage

Refer to the [documentation](#).
