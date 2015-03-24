from wishlib import inside_maya, inside_softimage

if inside_maya():
    from .m_utils import *
elif inside_softimage():
    from.si_utils import *
