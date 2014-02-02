import numpy as np
from .. import colors
from ...db import ChemlabDB
from .base import AbstractRenderer
from .sphere import SphereRenderer
from .sphere_imp import SphereImpostorRenderer
from .point import PointRenderer


vdw_dict = ChemlabDB().get("data", 'vdwdict')

class AtomRenderer(AbstractRenderer):
    """Render atoms by using different rendering methods.
    
    **Parameters**
    
    widget:
        The parent QChemlabWidget
    r_array: np.ndarray((NATOMS, 3), dtype=float)
        The atomic coordinate array
    type_array: np.ndarray((NATOMS, 3), dtype=object)
        An array containing all the atomic symbols like `Ar`, `H`, `O`.
        If the atomic type is unknown, use the `Xx` symbol.
    backend: "impostors" | "polygons" | "points"
        You can choose the rendering method between the sphere impostors, 
        polygonal sphere and points.
    
        .. seealso: :py:class:`~chemlab.graphics.renderers.SphereRenderer`
                    :py:class:`~chemlab.graphics.renderers.SphereImpostorRenderer`
                    :py:class:`~chemlab.graphics.renderers.PointRenderer`
    
    color_scheme: dict, should contain the 'Xx' key,value pair
       A dictionary mapping atom types to colors. By default it is the color
       scheme provided by `chemlab.graphics.colors.default_atom_map`. The 'Xx'
       symbol value is taken as the default color.
    
    radii_map: dict, should contain the 'Xx' key,value pair.
       A dictionary mapping atom types to radii. The default is the
       mapping contained in `chemlab.db.vdw.vdw_dict`
    
    """

    def __init__(self, widget, r_array, type_array,
                 backend='impostors',
                 color_scheme=colors.default_atom_map,
                 radii_map=vdw_dict,
                 shading='phong'):
        radii = []
        colorlist = []
        natoms = len(r_array)

        for i in range(natoms):
            radii.append(radii_map[type_array[i]])
            colorlist.append(color_scheme.get(type_array[i],
                                        color_scheme['Xx']))
        self.radii = radii        
        self.colors = np.array(colorlist, dtype='uint8')
        if backend == 'polygons':
            self.sr = SphereRenderer(widget, r_array, radii, colorlist,
                                     shading = shading)
            
        elif backend == 'impostors':
            self.sr = SphereImpostorRenderer(widget, r_array, radii,
                                             colorlist, shading=shading)
        elif backend == 'points':
            self.sr = PointRenderer(widget, r_array, colorlist)
        else:
            raise Exception("No backend %s available. Choose between polygons, impostors or points" % backend)

    def draw(self):
        self.sr.draw()
    
    def update_positions(self, r_array):
        """Update the atomic positions
        """

        self.sr.update_positions(r_array)
    
    def update_colors(self, cols):
        self.sr.update_colors(cols)
        
    def update_radii(self, radii):
        self.sr.update_radii(radii)
        
    def hide(self, mask):
        self.sr.hide(mask)
        
    def change_shading(self, shd):
        self.sr.change_shading(shd)
    