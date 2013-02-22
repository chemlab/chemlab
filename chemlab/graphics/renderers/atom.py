import numpy as np
from .. import colors
from ...data.vdw import vdw_dict
from .base import AbstractRenderer
from .sphere import SphereRenderer


class AtomRenderer(AbstractRenderer):
    def __init__(self, system):
        radii = []
        colorlist = []
        
        for i in range(system.n_atoms):
            radii.append(vdw_dict[system.type_array[i]])
            colorlist.append(colors.map.get(system.type_array[i], colors.light_grey))
        
        self.sr = SphereRenderer(system.r_array, radii, colorlist)

    def draw(self):
        self.sr.draw()
