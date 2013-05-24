import numpy as np

from .state import SystemHiddenState, SystemSelectionState
from ..renderers import SphereImpostorRenderer, CylinderImpostorRenderer
from ..pickers import SpherePicker, CylinderPicker

class BallAndStickRepresentation(object):
    
    def __init__(self, viewer, system):
        self.system = system
        self.viewer = viewer
        
        # Model classes
        self.hidden_state = SystemHiddenState(system)
        self.selection_state = SystemSelectionState(system)
        
        # Visualization classes
        self.sphere_renderer = self.viewer.add_renderer(SphereImpostorRenderer)
        self.cylinder_renderer = self.viewer.add_renderer(CylinderImpostorRenderer)
        
        self.sphere_highlight = self.viewer.add_renderer(SphereImpostorRenderer)
        self.cylinder_highlight = self.viewer.add_renderer(CylinderImpostorRenderer) 
        
        # User controls
        self.atom_picker = SpherePicker(self.viewer.widget, system.r_array,
                                        self.renderer.radii)        
        self.cylinder_picker = CylinderPicker(self.viewer.widget,
                                              system.r_array,
                                              system.get_bond_array(),
                                              cylinder_radii)
        
        self.hidden_state.atom_changed.connect(self.on_atom_hidden_changed)
        self.hidden_state.bond_changed.connect(self.on_bond_hidden_changed)
        
        self.selection_state.atom_changed.connect(self.on_atom_selection_changed)
        self.selection_state.bond_changed.connect(self.on_bond_selection_changed)

    def on_atom_hidden_changed(self):
        # When hidden state changes, the view update itself
        # Update the Renderers and the pickers
        pass
        
    def on_bond_hidden_changed(self):
        # When hidden state changes, the view update itself
        # Update the renderers and the pickers
        pass

    def on_atom_selection_changed(self):
        # When selection state changes, the view update itself
        pass
    
    def on_bond_selection_changed(self):
        # When selection state changes, the view update itself
        pass

    def on_click(self, x, y):
        # This is basically our controller
        x, y = self.viewer.widget.screen_to_normalized(x, y)
        
        # I need another picker
        at_indices = self.atom_picker.pick(x, y)
        bond_indices = self.bond_picler.pick(x, y)
        
        indices = at_indices + bond_indices
        
        if not indices:
            # Cancel selection
            self.make_selection([])
            self.last_modified = None
        else:
            self.last_modified = indices[0]
            self.make_selection([indices[0]], flip=True)
        
        self.viewer.widget.update()