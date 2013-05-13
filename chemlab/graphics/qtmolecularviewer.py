"""Trying to make a real molecular viewer
"""
from .qtviewer import QtViewer
from .renderers import AtomRenderer, SphereImpostorRenderer
import numpy as np

class QtMolecularViewer(QtViewer):
    def __init__(self, system):
        super(QtMolecularViewer, self).__init__()
        self.system = system
        
        self.rep = self.add_renderer(AtomRenderer, system.r_array,
                                     system.type_array)

    def make_selection(self, indices, additive=False):
        self.selection = indices
        self.highlight(self, indices)
    
    def highlight(self, indices):
        radius = 0.2
        # Make some bigger transparent spheres
        pos = self.system.r_array[indices]
        radii = [radius]*len(indices)
        cols = np.array([(255, 255, 0, 100)] * len(indices))
        
        self.highl_rend = self.add_renderer(SphereImpostorRenderer,
                                            pos, radii, cols,
                                            transparent=True)
    