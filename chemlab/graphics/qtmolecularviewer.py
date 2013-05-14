"""Trying to make a real molecular viewer
"""
from .qtviewer import QtViewer
from .renderers import AtomRenderer, SphereImpostorRenderer
from .pickers import SpherePicker
import numpy as np

class QtMolecularViewer(QtViewer):
    def __init__(self, system):
        super(QtMolecularViewer, self).__init__()
        self.system = system
        
        self.rep = self.add_renderer(AtomRenderer, system.r_array,
                                     system.type_array)
        self.picker = SpherePicker(self.widget, system.r_array,
                                   self.rep.radii)        
        
        self.widget.clicked.connect(self.on_click)
        self.selection = []
        
        self.highl_rend = None

    def is_selected(self, index):
        return index in self.selection
        
    def make_selection(self, indices, additive=False):
        if additive:
            self.selection = set(self.selection) ^ set(indices)
        else:
            self.selection = indices
            
        self.selection = list(set(self.selection)) # Uniquify
        
        self.highlight(self.selection)
    
    def highlight(self, indices):
        if not indices:
            self.remove_renderer(self.highl_rend)
            self.highl_rend = None
        
        # Make some bigger transparent spheres
        pos = self.system.r_array[indices]
        radii = [self.rep.radii[i]+0.01 for i in indices]
        cols = np.array([(255, 255, 0, 100)] * len(indices))
        print 'adding_renderers', indices
        if self.highl_rend:
            self.remove_renderer(self.highl_rend)
            
        self.highl_rend = self.add_renderer(SphereImpostorRenderer,
                                            pos, radii, cols,
                                            transparent=True)

    def on_click(self, evt):
        x, y = self.widget.screen_to_normalized(evt.x(), evt.y())
        indices = self.picker.pick(x, y)
        if not indices:
            # Cancel selection
            self.make_selection([])
        else:
            self.make_selection([indices[0]], additive=True)
        
        self.widget.update()
    

