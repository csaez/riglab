import logging
from maya import cmds
from riglab import cache
from riglab.rig import Rig


def list_rigs(name="C_*_grp"):
    for n in cache.scene.rigs.keys():
        if not exists(n):
            del cache.scene.rigs[n]
    for n in cmds.ls(name, type="transform"):
        if n not in cache.scene.rigs.keys():
            cache.scene.rigs[n] = Rig(n)
    return cache.scene.rigs.keys()


def get_rig(rig_name):
    rig = cache.scene.rigs.get(rig_name, Rig(rig_name))
    cache.scene.rigs[rig.name] = rig
    return rig


def get_rigs():
    return cache.scene.rigs.values()


def new_rig(rig_name):
    if exists(rig_name):
        logging.error("{} rig already exists".format(rig_name))
        return None
    rig = cache.scene.rigs[rig_name] = Rig(rig_name)
    return rig


def delete_rig(name):
    if exists(name):
        rig = get_rig(name)
        cmds.remove(rig.owner)
        del cache.scene.rigs[name]


def exists(name):
    cmds.exists(name)
    return True


def clear_cache():
    cache.scene = dict()

clear_cache()
__all__ = ("list_rigs", "get_rig", "get_rigs", "new_rig", "delete_rig",
           "exists", "clear_cache")
