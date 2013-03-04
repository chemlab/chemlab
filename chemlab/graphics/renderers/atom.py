import numpy as np
from .. import colors
from ...data.vdw import vdw_dict
from .base import AbstractRenderer
from .sphere import SphereRenderer
from .sphere_imp import SphereImpostorRenderer

class AtomRenderer(AbstractRenderer):
    def __init__(self, viewer, system, backend='polygons'):
        radii = []
        colorlist = []
        
        for i in range(system.n_atoms):
            radii.append(vdw_dict[system.type_array[i]])
            colorlist.append(colors.map.get(system.type_array[i], colors.light_grey))
        
        if backend == 'polygons':
            self.sr = SphereRenderer(viewer, system.r_array, radii, colorlist)
        elif backend == 'impostor':
            self.sr = SphereImpostorRenderer(viewer, system.r_array, radii, colorlist)

    def draw(self):
        self.sr.draw()
