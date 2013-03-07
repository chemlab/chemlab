import numpy as np
from .. import colors
from ...data.vdw import vdw_dict
from .base import AbstractRenderer
from .sphere import SphereRenderer
from .sphere_imp import SphereImpostorRenderer
from .point import PointRenderer

class AtomRenderer(AbstractRenderer):
    def __init__(self, viewer, system, type='polygons'):
        radii = []
        colorlist = []
        
        for i in range(system.n_atoms):
            radii.append(vdw_dict[system.type_array[i]])
            colorlist.append(colors.map.get(system.type_array[i], colors.light_grey))
        
        if type == 'polygons':
            self.sr = SphereRenderer(viewer, system.r_array, radii, colorlist)
        elif type == 'impostor':
            self.sr = SphereImpostorRenderer(viewer, system.r_array, radii, colorlist)
        elif type == 'points':
            self.sr = PointRenderer(viewer, system.r_array, colorlist)

    def draw(self):
        self.sr.draw()
    
    def update_positions(self, r_array):
        self.sr.update_positions(r_array)