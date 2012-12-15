import numpy as np
import pyglet.gl

from pyglet.graphics.vertexbuffer import VertexBufferObject
from pyglet.gl import *

from .. import colors
from ...data.vdw import vdw_dict
from ..optshapes import OptSphere
from ..gletools.shapes import Arrow
from .sphere import SphereRenderer


class AtomRenderer(SphereRenderer):
    def __init__(self, atoms):
        radii = [vdw_dict[atom.type] for atom in atoms]
        colorlist = [colors.map.get(atom.type, colors.light_grey) for atom in atoms]
        poslist = [at.coords for at in atoms]
        
        super(AtomRenderer, self).__init__(poslist, radii, colorlist)

