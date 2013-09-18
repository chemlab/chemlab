import numpy as np
import itertools

from .obsarray import obsarray as obsarray
from .state import SystemHiddenState, SystemSelectionState
from ...graphics.renderers import (SphereImpostorRenderer, CylinderImpostorRenderer,
                         AtomRenderer, BondRenderer)
from ...graphics import colors
from ...graphics.pickers import SpherePicker, CylinderPicker
from ...db import ChemlabDB
from ...graphics.postprocessing import GlowEffect

from PyQt4 import QtCore

cdb = ChemlabDB()
vdw_radii = cdb.get('data', 'vdwdict')
elements = cdb.get('data', 'elements')


class BallAndStickRepresentation(object):
    
    @property
    def atom_colors(self):
        return self._atom_colors
    
    @atom_colors.setter
    def atom_colors(self, value):
        self._atom_colors = obsarray(value)
        self._atom_colors.changed.connect(self.on_atom_colors_changed)
        self.on_atom_colors_changed()

    def on_atom_colors_changed(self):
        print 'Updating colors'
        self.atom_renderer.update_colors(self._atom_colors._arr)
        self.on_atom_selection_changed() # Hack
        
        self.viewer.widget.update()
        
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
        self.default_colors = self.atom_renderer.colors.copy()
        
        self.atom_radii = self.atom_renderer.radii
        self.atom_colors = self.atom_renderer.colors
        
        self.bond_renderer = self.viewer.add_renderer(BondRenderer,
                                                      system.bonds, system.r_array,
                                                      system.type_array, style='impostors')
        
        self.scale_factors = np.ones_like(self.atom_renderer.radii)
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

        self.glow_timer = QtCore.QTimer()
        
    def _gen_atom_renderer(self):
        pass
        
    def _gen_cylinder_renderer(self):
        pass
    
    def hide(self):
        # Take current selection and hide it
        self.hidden_state.hide_atoms(self.selection_state.atom_selection, mode='additive')
        
    def update_scale_factors(self, scalefac):
        self.scale_factors = scalefac
        radii = self.atom_radii * scalefac
        self.atom_renderer.update_radii(radii)
        
    def update_positions(self, r_array):
        self.atom_renderer.update_positions(r_array)
        self.bond_renderer.update_positions(r_array)
        
        # User controls
        self.atom_picker = SpherePicker(self.viewer.widget, r_array,
                                        self.atom_renderer.radii)
        self.bond_picker = CylinderPicker(self.viewer.widget,
                                          r_array.take(self.system.bonds, axis=0),
                                          self.bond_radii)

    def on_atom_hidden_changed(self):
        # When hidden state changes, the view update itself
        # Update the Renderers and the pickers
        no_sel = self.selection_state.atom_selection
        
        # Take everything else
        sel = np.ones(self.system.n_atoms, dtype='bool')
        sel[self.hidden_state.atom_hidden_mask] = False
        sel[no_sel] = False
        
        self.atom_renderer.hide(sel)
        
        # Reset selection
        self.selection_state.select_atoms([])
        self.viewer.update()
        
    def on_bond_hidden_changed(self):
        # When hidden state changes, the view update itself
        # Update the renderers and the pickers
        sel = self.hidden_state.bond_selection

    def on_atom_selection_changed(self):
        #self.glow_timer.stop()
        # When selection state changes, the view update itself
        sel = self.selection_state.atom_selection
        cols = self.atom_colors.copy()
        
        cols[sel, -1] = 50
                    
        self.atom_renderer.update_colors(cols)
        self.viewer.update()
    
    def on_bond_selection_changed(self):
        # When selection state changes, the view update itself
        if self.system.n_bonds == 0:
            return
        
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