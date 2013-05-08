from .base import AbstractRenderer
from .atom import AtomRenderer
from .bond import BondRenderer
from .sphere_imp import SphereImpostorRenderer
from .cylinder_imp import CylinderImpostorRenderer

from ...db import ChemlabDB
from .. import colors
import numpy as np

cdb = ChemlabDB()

class WireframeRenderer(AbstractRenderer):
    '''
        Render a wireframe representation of a series of
        coordinates and bonds.
    
        .. image:: /_static/wireframe_renderer.png
                 :width: 300px
    
        **Parameters**
    
        widget:
           The parent QChemlabWidget
        r_array: np.ndarray((NATOMS, 3), dtype=float)
            The coordinate array
        type_array: np.ndarray((NATOMS, 3), dtype=object)
            An array containing all the atomic symbols like `Ar`, `H`, `O`.
            If the atomic type is unknown, use the `Xx` symbol.
        bonds: np.ndarray((NBONDS, 2), dtype=int)
            An array of integer pairs that represent the bonds.

    '''

    def __init__(self, widget, r_array, type_array, bonds):
        super(WireframeRenderer, self).__init__(widget)
        vdw_dict = cdb.get("data", "vdwdict")        
        
        scale = 0.3
        for k in vdw_dict:
            vdw_dict[k] = vdw_dict[k] * scale
        
        self.has_bonds = len(bonds) > 0
        self.ar = SphereImpostorRenderer(widget, r_array, [0.01] * len(r_array),
                                         colors.black * len(r_array))
        
        self.bonds = bonds
        
        if self.has_bonds:
            starts = r_array[bonds[:, 0]]
            ends = r_array[bonds[:, 1]]
            bounds = np.empty((len(starts), 2, 3))
            
            bounds[:, 0, :] = starts
            bounds[:, 1, :] = ends
            
            self.br = CylinderImpostorRenderer(widget, bounds,
                                               [0.01] * len(bounds),
                                               [colors.black] * len(bounds))

        
    def draw(self):
        self.ar.draw()
        
        if self.has_bonds:
            self.br.draw()

    def update_positions(self, r_array):
        self.ar.update_positions(r_array)
        
        if self.has_bonds:
            bonds = self.bonds
            starts = r_array[bonds[:, 0]]
            ends = r_array[bonds[:, 1]]
            bounds = np.empty((len(starts), 2, 3))
            
            bounds[:, 0, :] = starts
            bounds[:, 1, :] = ends
            
            self.br.update_bounds(bounds)