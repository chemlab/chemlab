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
        
        self.keys = {}
        
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

    def keyPressEvent(self, evt):
        if evt.key() == Qt.Key_A:
            if 'a' in self.keys:
                self.keys['a']()

        if evt.key() == Qt.Key_S:
            if 's' in self.keys:
                self.keys['s']()
        return super(QtMolecularViewer, self).keyPressEvent(evt)
        
class VdWRepresentation(object):
    
    def __init__(self, viewer, system):
        self.system = system
        self.viewer = viewer
        self.renderer = self.viewer.add_renderer(AtomRenderer, system.r_array,
                                                 system.type_array)
        self.picker = SpherePicker(self.viewer.widget, system.r_array,
                                   self.renderer.radii)        
        
        self.selection_mask = np.zeros(self.system.n_atoms, dtype='bool')
        self.hidden_mask = np.zeros(self.system.n_atoms, dtype='bool')
        
        self.last_modified = None
        
        self.highl_rend = None

    @property
    def selection(self):
        return self.selection_mask.nonzero()[0].tolist()
        
    def make_selection(self, indices, additive=False, flip=False):
        if additive:
            self.selection_mask[indices] = True
        elif flip:
            self.selection_mask[indices] = np.logical_not(self.selection_mask[indices])

        else:
            self.selection_mask[:] = False
            self.selection_mask[indices] = True

        self.highlight(self.selection)
    
    def scale_radii(self, selection, scale_factor):
        self.renderer.radii = np.array(self.renderer.radii)
        self.renderer.radii[selection] *= scale_factor
        self.renderer.sr.update_radii(self.renderer.radii)
        self.picker.radii = self.renderer.radii
        
    def highlight(self, indices):
        if not indices:
            try:
                self.viewer.remove_renderer(self.highl_rend)
            except:
                pass
            self.highl_rend = None
        
        # Make some bigger transparent spheres
        pos = self.system.r_array[indices]
        radii = np.array([0.3] * len(indices))#[self.renderer.radii[i]+0.01 for i in indices]
        cols = np.array([(255, 255, 0, 100)] * len(indices))
        if self.highl_rend:
            self.viewer.remove_renderer(self.highl_rend)
            
        self.highl_rend = self.viewer.add_renderer(SphereImpostorRenderer,
                                                   pos, radii, cols,
                                                   transparent=True)
        
    def hide(self, selection, additive=True):
        if additive:
            self.hidden_mask[selection] = True
        else:
            self.hidden_mask[:] = False
            self.hidden_mask[selection] = True
        
        mask = np.logical_not(self.hidden_mask)
        self.viewer.remove_renderer(self.renderer)
        self.renderer = self.viewer.add_renderer(AtomRenderer,
                                                 self.system.r_array[mask],
                                                 self.system.type_array[mask])
        #self.picker = SpherePicker(self.viewer.widget, self.system.r_array[mask],
        #                           np.array(self.renderer.radii))   
        
        self.viewer.remove_renderer(self.highl_rend)
        self.make_selection([])

    
    def on_click(self, x, y):
        x, y = self.viewer.widget.screen_to_normalized(x, y)
        indices = self.picker.pick(x, y)
        if not indices:
            # Cancel selection
            self.make_selection([])
            self.last_modified = None
        else:
            # Do not pick if hidden
            indices = np.array(indices)[~self.hidden_mask[indices]].tolist()
            
            if not indices:
                self.make_selection([])
                self.last_modified = None
            
            self.last_modified = indices[0]
            self.make_selection([indices[0]], flip=True)
        
        self.viewer.widget.update()

class BallAndStickRepresentation(object):
    
    def __init__(self, viewer, system):
        self.system = system
        self.viewer = viewer
        self.sphere_renderer = self.viewer.add_renderer(SphereImpostorRenderer)
        self.cylinder_renderer = self.viewer.add_renderer(CylinderImpostorRenderer)
        
        
        self.atom_picker = SpherePicker(self.viewer.widget, system.r_array,
                                   self.renderer.radii)        
        
        self.cylinder_picker = CylinderPicker(self.viewer.widget, system.r_array,
                                              system.get_bond_array(), cylinder_radii)
        
        self.selection_mask = np.zeros(self.system.n_atoms, dtype='bool')
        self.hidden_mask = np.zeros(self.system.n_atoms, dtype='bool')
        
        self.last_modified = None
        self.highlight_renderer = None

    @property
    def selection(self):
        return self.selection_mask.nonzero()[0].tolist()
        
    # Rename this in atom_selection
    def make_selection(self, indices, additive=False, flip=False):
        if additive:
            self.selection_mask[indices] = True
        elif flip:
            self.selection_mask[indices] = np.logical_not(self.selection_mask[indices])

        else:
            self.selection_mask[:] = False
            self.selection_mask[indices] = True

        self.highlight(self.selection)
    
    # Need to rename another one in bond_selection
    def bond_selection(self, bond_indices, additive=False, flip=False):
        pass
    
    def scale_radii(self, selection, scale_factor):
        self.renderer.radii = np.array(self.renderer.radii)
        self.renderer.radii[selection] *= scale_factor
        self.renderer.sr.update_radii(self.renderer.radii)
        self.picker.radii = self.renderer.radii
        
    def highlight(self, indices):
        if not indices:
            try:
                self.viewer.remove_renderer(self.highl_rend)
            except:
                pass
            self.highl_rend = None
        
        # Make some bigger transparent spheres
        pos = self.system.r_array[indices]
        radii = np.array([0.3] * len(indices))#[self.renderer.radii[i]+0.01 for i in indices]
        cols = np.array([(255, 255, 0, 100)] * len(indices))
        if self.highl_rend:
            self.viewer.remove_renderer(self.highl_rend)
            
        self.highl_rend = self.viewer.add_renderer(SphereImpostorRenderer,
                                                   pos, radii, cols,
                                                   transparent=True)
        
    def hide(self, selection, additive=True):
        if additive:
            self.hidden_mask[selection] = True
        else:
            self.hidden_mask[:] = False
            self.hidden_mask[selection] = True
        
        mask = np.logical_not(self.hidden_mask)
        self.viewer.remove_renderer(self.renderer)
        self.renderer = self.viewer.add_renderer(AtomRenderer,
                                                 self.system.r_array[mask],
                                                 self.system.type_array[mask])
        self.picker = SpherePicker(self.viewer.widget, self.system.r_array[mask],
                                   np.array(self.renderer.radii))   
        
        self.viewer.remove_renderer(self.highl_rend)
        self.make_selection([])

    
    def on_click(self, x, y):
        x, y = self.viewer.widget.screen_to_normalized(x, y)
        indices = self.picker.pick(x, y)
        if not indices:
            # Cancel selection
            self.make_selection([])
            self.last_modified = None
        else:
            self.last_modified = indices[0]
            self.make_selection([indices[0]], flip=True)
        
        self.viewer.widget.update()