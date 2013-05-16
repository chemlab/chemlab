"""Trying to make a real molecular viewer
"""
from PySide import QtGui
from PySide.QtCore import Qt

from .qtviewer import QtViewer
from .renderers import AtomRenderer, SphereImpostorRenderer
from .pickers import SpherePicker
import numpy as np



class QtMolecularViewer(QtViewer):
    def __init__(self, system):
        super(QtMolecularViewer, self).__init__()
        self.actions = {}
        
        self.system = system
        self.representation = VdWRepresentation(self, system)
        self.widget.clicked.connect(self.on_click)
        # Let's add some dock
        self.controls = QtGui.QDockWidget()
        # Eliminate the dock titlebar
        title_widget = QtGui.QWidget(self)
        self.controls.setTitleBarWidget(title_widget)
        hb = QtGui.QHBoxLayout() # For controls
        

        
        self.actions['action1'] = QtGui.QPushButton('action1')
        self.actions['action2'] = QtGui.QPushButton('action2')
        
        [hb.addWidget(w) for w in self.actions.values()]
        wrapper = QtGui.QWidget()
        wrapper.setLayout(hb)
        self.controls.setWidget(wrapper)
        self.addDockWidget(Qt.DockWidgetArea(Qt.BottomDockWidgetArea),
                           self.controls)
        
        
    def on_click(self, evt):
        self.representation.on_click(evt.x(), evt.y())

class VdWRepresentation(object):
    
    def __init__(self, viewer, system):
        self.system = system
        self.viewer = viewer
        self.renderer = self.viewer.add_renderer(AtomRenderer, system.r_array,
                                                 system.type_array)
        self.picker = SpherePicker(self.viewer.widget, system.r_array,
                                   self.renderer.radii)        
        self.selection = []
        
        self.highl_rend = None

    def make_selection(self, indices, additive=False):
        if additive:
            self.selection = set(self.selection) ^ set(indices)
        else:
            self.selection = indices
            
        self.selection = list(set(self.selection)) # Uniquify
        
        self.highlight(self.selection)
    
    def highlight(self, indices):
        if not indices:
            try:
                self.viewer.remove_renderer(self.highl_rend)
            except:
                pass
            self.highl_rend = None
        
        # Make some bigger transparent spheres
        pos = self.system.r_array[indices]
        radii = [self.renderer.radii[i]+0.01 for i in indices]
        cols = np.array([(255, 255, 0, 100)] * len(indices))
        if self.highl_rend:
            self.viewer.remove_renderer(self.highl_rend)
            
        self.highl_rend = self.viewer.add_renderer(SphereImpostorRenderer,
                                                   pos, radii, cols,
                                                   transparent=True)
    
    def on_click(self, x, y):
        x, y = self.viewer.widget.screen_to_normalized(x, y)
        indices = self.picker.pick(x, y)
        if not indices:
            # Cancel selection
            self.make_selection([])
        else:
            self.make_selection([indices[0]], additive=True)
        
        self.viewer.widget.update()
