import logging
from riglab import cache
#from riglab.rig import Rig
#from maya import cmds


class Rig(object):
    pass


def list_rigs(pattern="C_*_grp"):
    for n in cache.scene.rigs.keys():
        if not exists(n):
            del cache.scene.rigs[n]
    for n in cmds.ls(pattern, type="transform"):
        if n not in cache.scene.rigs.keys():
            cache.scene.rigs[n] = Rig(n)
    return cache.scene.rigs.keys()


def get_rig(name):
    rig = cache.scene.rigs.get(name, Rig(name))
    cache.scene.rigs[name] = rig
    return rig


def get_rigs():
    return cache.scene.rigs.values()


def new_rig(name):
    if exists(name):
        logging.error("{} rig already exists".format(name))
        return None
    cache.scene.rigs[name] = Rig(name)
    return cache.scene.rigs[name]


def delete_rig(name):
    if exists(name):
        rig = get_rig(name)
        cmds.remove(rig.owner)
        del cache.scene.rigs[name]


def exists(name):
    return True


def clear_cache():
    cache.scene = dict()

clear_cache()
__all__ = ("list_rigs", "get_rig", "get_rigs", "new_rig", "delete_rig",
           "exists", "clear_cache")
