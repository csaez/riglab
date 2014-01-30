# This file is part of riglab.
# Copyright (C) 2014  Cesar Saez

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from .base import Base
from ..manipulator import Manipulator
from .. import utils


class FK(Base):

    def custom_inputs(self):
        super(FK, self).custom_inputs()

    def custom_anim(self):
        super(FK, self).custom_build()
        anim = [Manipulator.new(parent=self.input.get("root"))]
        anim[0].owner = {"obj": self.obj, "class": self.classname}
        # apply shape and color from convention
        anim[0].icon.shape = self.shape_color.get("fkIcon")
        anim[0].icon.color = self.shape_color.get(self.side)[0]
        # OPTIMIZATION: duplicate instead of create a new one
        copies = len(self.input.get("skeleton")) - 2
        if copies >= 1:
            anim.extend(anim[0].duplicate(copies))
        # align
        if self.helper.get("curve"):
            data = zip(*utils.curve_data(self.helper.get("curve")))
            utils.align_matrix4(anim[0].zero, data[0][0])
            for i, (matrix, length) in enumerate(data[:-1]):
                m = anim[i]
                if i > 0:
                    m.parent = anim[i - 1].anim
                utils.align_matrix4(m.zero, matrix)
                m.icon.sclx = length
        else:  # align with the first bone
            anim[0].align(self.input["skeleton"][0])
        # rename
        for i, each in enumerate(anim):
            each.rename(self.name, i, side=self.side)
            self.input.get("anim").append(each.anim)
            self.helper.get("hidden").extend([each.zero, each.space])
        self.input["anim"] = [x.anim for x in anim]

    def custom_build(self):
        super(FK, self).custom_build()
        skeleton = self.input.get("skeleton")
        if len(skeleton) > 1:
            skeleton = self.input.get("skeleton")[:-1]
            if self.reversed():
                skeleton = self.input.get("skeleton")[1:]
        for i, bone in enumerate(skeleton):
            anim = self.input["anim"][i]
            self.output["tm"][i].Kinematics.AddConstraint("Pose", anim)
            # set snap reference
            self.get_manipulator(anim.FullName).snap_ref(bone)
        # connect root
        self.get_manipulator(self.input["anim"][0].FullName).snap_ref(
            self.input["skeleton"][0])

    @staticmethod
    def validate(skeleton):
        return len(skeleton) >= 1
