from .base import AbstractRenderer
from . import CylinderRenderer, LineRenderer, CylinderImpostorRenderer
import numpy as np
from chemlab.graphics.colors import default_atom_map

class BondRenderer(AbstractRenderer):
    '''
        Render chemical bonds as cylinders or lines.

        **Parameters**
    
        widget:
           The parent QChemlabWidget
        bonds: np.ndarray((NBONDS, 2), dtype=int)
            An array of integer pairs that represent the bonds.
        r_array: np.ndarray((NATOMS, 3), dtype=float)
            The coordinate array
        type_array: np.ndarray((NATOMS, 3), dtype=object)
            An array containing all the atomic symbols like `Ar`, `H`, `O`.
            If the atomic type is unknown, use the `Xx` symbol.
        radius: float, default=0.02
            The radius of the bonds
        style: "cylinders" | "lines"
            Whether to render the bonds as cylinders or lines.
    
    '''
    def __init__(self, widget, bonds, r_array, type_array, radius=0.02,
                 style="cylinders", shading='phong'):
        #super(BondRenderer, self).__init__(widget)
        
        self.bonds = bonds
        bounds_a, bounds_b = self._compute_bounds(r_array, bonds)
    
        radii = [radius] * len(bounds_a)

        colors_a = []
        colors_b = []

        for i, j in bonds:
            colors_a.append(
                default_atom_map.get(type_array[i],
                                 default_atom_map['Xx']))
            colors_b.append(
                default_atom_map.get(type_array[j],
                                 default_atom_map['Xx']))

        self.radii = radii
        self.colors_a = np.array(colors_a, 'uint8')
        self.colors_b = np.array(colors_b, 'uint8')
        
        if style == 'cylinders':
            self.cr1 = CylinderRenderer(widget, bounds_a, radii, colors_a)
            self.cr2 = CylinderRenderer(widget, bounds_b, radii, colors_b)
        elif style == 'lines':
            self.cr1 = LineRenderer(widget, bounds_a.flatten(),
                                    np.tile(colors_a, 2))
            self.cr2 = LineRenderer(widget, bounds_b.flatten(),
                                    np.tile(colors_b, 2))
        elif style == 'impostors':
            self.cr1 = CylinderImpostorRenderer(widget, bounds_a, radii,
                                                colors_a, shading=shading)
            self.cr2 = CylinderImpostorRenderer(widget, bounds_b, radii,
                                                colors_b, shading=shading)
        else:
            raise Exception("Available backends: cylinders, lines")
    
    def _compute_bounds(self, r_array, bonds):
        
        if len(bonds) == 0:
            return np.array([]), np.array([])
        
        starts = r_array[bonds[:,0]]
        ends = r_array[bonds[:,1]]
        middle = (starts + ends)/2 
    
        bounds_a = np.empty((len(bonds), 2, 3))
        bounds_a[:, 0, :] = starts
        bounds_a[:, 1, :] = middle
    
        bounds_b = np.empty((len(bonds), 2, 3))    
        bounds_b[:, 0, :] = middle
        bounds_b[:, 1, :] = ends
        
        return bounds_a, bounds_b
        
        
    def draw(self):
        self.cr1.draw()
        self.cr2.draw()

    def update_positions(self, r_array):
        bounds_a, bounds_b = self._compute_bounds(r_array, self.bonds)
        if bounds_a.size == 0 or bounds_b.size == 0:
            return
        
        self.cr1.update_bounds(bounds_a)
        self.cr2.update_bounds(bounds_b)

    def update_colors(self, colors_a, colors_b):
        self.colors_a = np.array(colors_a, 'uint8')
        self.colors_b = np.array(colors_b, 'uint8')
        
        self.cr1.update_colors(self.colors_a)
        self.cr2.update_colors(self.colors_b)
