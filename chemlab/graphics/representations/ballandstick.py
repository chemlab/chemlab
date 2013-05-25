import numpy as np
import itertools

from .state import SystemHiddenState, SystemSelectionState
from ..renderers import (SphereImpostorRenderer, CylinderImpostorRenderer,
                         AtomRenderer, BondRenderer)
from ..pickers import SpherePicker, CylinderPicker
from ...db import ChemlabDB

vdw_radii = ChemlabDB().get('data', 'vdwdict')

class BallAndStickRepresentation(object):
    
    def __init__(self, viewer, system):
        self.system = system
        self.viewer = viewer
        
        # Model classes
        self.hidden_state = SystemHiddenState(system)
        self.selection_state = SystemSelectionState(system)
        
        atom_scale = 0.4
        radii_map = {k: v * atom_scale for k, v in vdw_radii.items()}
        
        bonds = self.system.get_bond_array()
        
        # Visualization classes
        self.atom_renderer = self.viewer.add_renderer(AtomRenderer,
                                                      system.r_array,
                                                      system.type_array,
                                                      radii_map=radii_map)
        self.atom_radii = self.atom_renderer.radii
        
        self.bond_renderer = self.viewer.add_renderer(BondRenderer,
                                                      bonds, system.r_array,
                                                      system.type_array)
        self.bond_radii = self.bond_renderer.radii
        
        # Highlighting
        #self.atom_highlight = self.viewer.add_renderer(SphereImpostorRenderer)
        #self.bond_highlight = self.viewer.add_renderer(CylinderImpostorRenderer) 
        
        # User controls
        self.atom_picker = SpherePicker(self.viewer.widget, system.r_array,
                                        self.renderer.radii)
        
        self.cylinder_picker = CylinderPicker(self.viewer.widget,
                                              system.r_array,
                                              system.get_bond_array(),
                                              self.bond_radii)
        
        self.hidden_state.atom_changed.connect(self.on_atom_hidden_changed)
        self.hidden_state.bond_changed.connect(self.on_bond_hidden_changed)
        
        self.selection_state.atom_changed.connect(self.on_atom_selection_changed)
        self.selection_state.bond_changed.connect(self.on_bond_selection_changed)

    def _gen_atom_renderer(self):
        pass
        
    def _gen_cylinder_renderer(self):
        pass
    
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
        a_indices, a_dists = self.atom_picker.pick(x, y)
        b_indices, b_dists = self.bond_picler.pick(x, y)
        
        indices = list(itertools.chain(a_indices, b_indices))
        
        if not indices:
            # Cancel selection
            self.selection_state.select_atoms()
        else:
            # Determine the candidate
            dist_a = a_dists[0] if a_indices else float('inf')
            dist_b = b_dists[0] if b_indices else float('inf')
            
            if dist_a > dist_b:
                self.selection_state.select_atoms([dist_a], flip=True)
            else:
                self.selection_state.select_bonds([dist_b], flip=True)
            
        self.viewer.widget.update()