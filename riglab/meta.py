from maya import cmds


class Meta(object):

    def __init__(self, node):
        self.owner = node
        for key in cmds.listAttr(self.owner, ud=True) or tuple():
            attr = ".".join((self.owner, key))
            if cmds.getAttr(attr, typ=True) == "message":
                values = cmds.listConnections(attr) or tuple()
                value = values[0] if len(values) else None
            else:
                value = eval(cmds.getAttr(attr))
            setattr(self, key, value)

    def __setattr__(self, key, value):
        super(Meta, self).__setattr__(key, value)
        if key in ("owner", ):
            return
        attr = ".".join((self.owner, key))
        if cmds.objExists(attr):
            cmds.deleteAttr(".".join((self.owner, key)))
        if isinstance(value, basestring) and cmds.objExists(value):
            cmds.addAttr(self.owner, ln=key, at="message")
            cmds.connectAttr("{}.message".format(value), attr, f=True)
        else:
            cmds.addAttr(self.owner, ln=key, dt="string")
            cmds.setAttr(attr, repr(value), typ="string")

    def __delattr__(self, key):
        super(Meta, self).__delattr__(key)
        cmds.deleteAttr(".".join((self.owner, key)))


def test(meta_node):
    class Foo(Meta):

        def __init__(self, node):
            super(Foo, self).__init__(node)

    foo = Foo(meta_node)
    foo.string = "pCube1"
    foo.number = 39
    foo.iterable = range(10)
    foo.null = None

    bar = Foo(meta_node)
    assert bar.string == "pCube1"
    assert bar.number == 39
    assert bar.iterable == range(10)
    assert bar.null is None

test(cmds.ls(sl=True)[0])
