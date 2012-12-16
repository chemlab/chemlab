import numpy as np
from .. import colors
from ...data.vdw import vdw_dict
from .base import AbstractRenderer
from .sphere import SphereRenderer


class AtomRenderer(AbstractRenderer):
    def __init__(self, atoms):
        radii = [vdw_dict[atom.type] for atom in atoms]
        colorlist = [colors.map.get(atom.type, colors.light_grey)
                     for atom in atoms]
        poslist = [at.coords for at in atoms]
        
        self.sr = SphereRenderer(poslist, radii, colorlist)

    def draw(self):
        self.sr.draw()
