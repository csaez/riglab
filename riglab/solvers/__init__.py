from .fk import FK
from .ik import IK


def from_manipulator(manipulator):
    cls = globals().get(manipulator.owner.get("class"))
    obj = manipulator.owner.get("obj")
    if cls and obj:
        return cls(obj)
