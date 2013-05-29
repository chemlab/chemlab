import numpy as np
import itertools

from .state import SystemHiddenState, SystemSelectionState
from ..renderers import (SphereImpostorRenderer, CylinderImpostorRenderer,
                         AtomRenderer, BondRenderer)
from .. import colors
from ..pickers import SpherePicker, CylinderPicker
from ...db import ChemlabDB
from ..postprocessing import GlowEffect

cdb = ChemlabDB()
vdw_radii = cdb.get('data', 'vdwdict')
elements = cdb.get('data', 'elements')

class BallAndStickRepresentation(object):
    
    def __init__(self, viewer, system):
        self.system = system
        self.viewer = viewer
        
        # Model classes
        self.hidden_state = SystemHiddenState(system)
        self.selection_state = SystemSelectionState(system)
        
        atom_scale = 0.3
        radii_map = {k: v * atom_scale for k, v in vdw_radii.items()}
        
        # Visualization classes
        self.atom_renderer = self.viewer.add_renderer(AtomRenderer,
                                                      system.r_array,
                                                      system.type_array,
                                                      radii_map=radii_map)
        self.atom_radii = self.atom_renderer.radii
        self.atom_colors = self.atom_renderer.colors
        
        self.bond_renderer = self.viewer.add_renderer(BondRenderer,
                                                      system.bonds, system.r_array,
                                                      system.type_array, style='impostors')
        self.bond_radii = self.bond_renderer.radii
        self.bond_colors = self.bond_renderer.colors_a, self.bond_renderer.colors_b
        
        # For highlight, we'll see
        self.viewer.add_post_processing(GlowEffect)
        
        # User controls
        self.atom_picker = SpherePicker(self.viewer.widget, system.r_array,
                                        self.atom_renderer.radii)
        self.bond_picker = CylinderPicker(self.viewer.widget,
                                          system.r_array.take(system.bonds, axis=0),
                                          self.bond_radii)
        
        self.hidden_state.atom_mask_changed.connect(self.on_atom_hidden_changed)
        self.hidden_state.bond_mask_changed.connect(self.on_bond_hidden_changed)
        
        self.selection_state.atom_mask_changed.connect(self.on_atom_selection_changed)
        self.selection_state.bond_mask_changed.connect(self.on_bond_selection_changed)

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
        
        sel = self.selection_state.atom_selection
        cols = self.atom_colors.copy()
        cols[sel, -1] = 50
        self.atom_renderer.update_colors(cols)
        self.viewer.widget.update()
    
    def on_bond_selection_changed(self):
        # When selection state changes, the view update itself
        print('bond_selected', self.selection_state.bond_selection)
        sel = self.selection_state.bond_selection
        cols_a, cols_b = self.bond_colors
        cols_a = cols_a.copy()
        cols_b = cols_b.copy()
        
        cols_a[sel, -1] = 50
        cols_b[sel, -1] = 50
        
        self.bond_renderer.update_colors(cols_a, cols_b)
        
    def on_click(self, x, y):
        # This is basically our controller
        x, y = self.viewer.widget.screen_to_normalized(x, y)
        
        # I need another picker
        a_indices, a_dists = self.atom_picker.pick(x, y)
        b_indices, b_dists = self.bond_picker.pick(x, y)
        
        indices = list(itertools.chain(a_indices, b_indices))
        
        #print 'A', a_indices, a_dists
        #print 'B', b_indices, b_dists
        
        if not indices:
            # Cancel selection
            self.selection_state.select_atoms([], mode='exclusive')
            self.selection_state.select_bonds([], mode='exclusive')
        else:
            # Determine the candidate
            dist_a = a_dists[0] if a_indices else float('inf')
            dist_b = b_dists[0] if b_indices else float('inf')
            
            if dist_a < dist_b:
                self.selection_state.select_atoms([a_indices[0]], mode='flip')
            else:
                self.selection_state.select_bonds([b_indices[0]], mode='flip')
        
        self.viewer.widget.update()