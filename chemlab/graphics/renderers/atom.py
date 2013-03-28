import numpy as np
from .. import colors
from ...data.vdw import vdw_dict
from .base import AbstractRenderer
from .sphere import SphereRenderer
from .sphere_imp import SphereImpostorRenderer
from .point import PointRenderer

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
       mapping contained in `chemlab.data.vdw.vdw_dict`
    
    """

    def __init__(self, widget, r_array, type_array,
                 backend='impostors',
                 color_scheme=colors.default_atom_map,
                 radii_map=vdw_dict):
        radii = []
        colorlist = []
        
        color_scheme = color_scheme.copy()
        # Making the guy case_insensitive
        for k,v in color_scheme.items():
            color_scheme[k.lower()] = v
            color_scheme[k.upper()] = v
        
        natoms = len(r_array)
        
        for i in range(natoms):
            radii.append(vdw_dict[type_array[i]])
            colorlist.append(color_scheme.get(type_array[i],
                                        color_scheme['Xx']))
        
        if backend == 'polygons':
            self.sr = SphereRenderer(widget, r_array, radii, colorlist)
        elif backend == 'impostors':
            self.sr = SphereImpostorRenderer(widget, r_array, radii, colorlist)
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