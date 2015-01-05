import numpy as np
import itertools

from .obsarray import obsarray as obsarray
from .state import SystemHiddenState, SystemSelectionState, ArrayState
from .state import Selection
from ...graphics.renderers import (SphereImpostorRenderer,
                                   CylinderImpostorRenderer, AtomRenderer,
                                   BondRenderer, BoxRenderer)
from ...graphics import colors
from ...graphics.pickers import SpherePicker, CylinderPicker
from ...db import ChemlabDB
from ...graphics.postprocessing import GlowEffect

from PyQt4 import QtCore

cdb = ChemlabDB()
vdw_radii = cdb.get('data', 'vdwdict')
elements = cdb.get('data', 'elements')

from ..events import Model, Event

class BallAndStickRepresentation(Model):
    

    atom_clicked = Event()
    bond_clicked = Event()
    
    @property
    def atom_colors(self):
        return self.color_state
    
    @atom_colors.setter
    def atom_colors(self, value):
        self.color_state.array = value
        self.on_atom_colors_changed()

    def on_atom_colors_changed(self):
        self.atom_renderer.update_colors(self.color_state.array)
        self.on_atom_selection_changed() # Hack
        
        self.viewer.widget.update()
        
    def __init__(self, viewer, system):
        self._callbacks = {} # TODO: This is because the model class doesnt work
        self.system = system
        self.viewer = viewer
        
        self.color_scheme = colors.default_atom_map
        

        
        # Model classes
        self.hidden_state = {'atoms': Selection([], system.n_atoms),
                             'bonds': Selection([], system.n_bonds),
                             'box': Selection([], 1)}
        
        self.selection_state = {'atoms': Selection([], system.n_atoms),
                                'bonds': Selection([], system.n_bonds),
                                'box': Selection([], 1)}
        
        self.color_state = ArrayState([colors.default_atom_map.get(t, colors.deep_pink) for t in system.type_array])
        self.radii_state = ArrayState([vdw_radii.get(t) * 0.3  for t in system.type_array])
        
        # Visualization classes
        self.atom_renderer = self.viewer.add_renderer(SphereImpostorRenderer,
                                                      system.r_array,
                                                      self.radii_state.array,
                                                      self.color_state.array)

        self.bond_renderer = self.viewer.add_renderer(BondRenderer,
                                                      system.bonds, system.r_array,
                                                      system.type_array, style='impostors')
        
        
        self.box_renderer = self.viewer.add_renderer(BoxRenderer,
                                                     system.box_vectors,
                                                     color=(100, 100, 100, 255))
        self.scale_factors = np.ones_like(self.radii_state.array)
        
        self.bond_radii = np.array(self.bond_renderer.radii)
        self.bond_colors = self.bond_renderer.colors_a, self.bond_renderer.colors_b
        
        # For highlight, we'll see
        self.viewer.add_post_processing(GlowEffect)
        
        # User controls
        self.atom_picker = SpherePicker(self.viewer.widget, system.r_array,
                                        self.radii_state.array)
        
        self.bond_picker = CylinderPicker(self.viewer.widget,
                                          system.r_array.take(system.bonds, axis=0),
                                          self.bond_radii)
        
        self.color_state.changed.connect(self.on_atom_colors_changed)
        
        self.glow_timer = QtCore.QTimer()

    def visible_atoms(self):
        return self.hidden_state['atoms'].invert().indices
        
    def _gen_atom_renderer(self):
        pass
        
    def _gen_cylinder_renderer(self):
        pass
    
    def update_box(self, vectors):
        self.box_renderer.vectors = vectors.copy()
        
    def update_scale_factors(self, scalefac):
        self.scale_factors = scalefac
        radii = np.array(self.radii_state.array) * scalefac
        self.atom_renderer.update_radii(radii)
        self.viewer.widget.update()
        
    def update_positions(self, r_array):

        self.bond_renderer.update_positions(r_array)
        self.atom_renderer.update_positions(r_array)
        

        # User controls
        hmsk = self.hidden_state['bonds'].invert().indices # Visible
        va = self.visible_atoms()
        self.atom_picker = SpherePicker(self.viewer.widget, r_array[va],
                                        self.radii_state.array[va])
        
        self.bond_picker = CylinderPicker(self.viewer.widget,
                                          r_array.take(self.system.bonds[hmsk], axis=0),
                                          self.bond_radii[hmsk])

    def on_atom_hidden_changed(self):
        # When hidden state changes, the view update itself
        # Update the Renderers and the pickers
        #no_sel = self.selection_state['atoms'].indices
        
        # Take everything else
        #sel = np.ones(self.system.n_atoms, dtype='bool')
        #sel[self.hidden_state['atoms'].mask] = False
        #sel[no_sel] = False
        
        sel = self.hidden_state['atoms'].invert().mask
        
        self.atom_renderer.hide(sel)
        
        # Pickers
        self.atom_picker = SpherePicker(self.viewer.widget, self.system.r_array[sel],
                                        self.radii_state.array[sel])
        
        # Reset selection
        self.selection_state['atoms'] = Selection([], self.system.n_atoms)
        self.on_atom_selection_changed()
        
        self.viewer.update()
        
    def on_bond_hidden_changed(self):
        # When hidden state changes, the view update itself
        # Update the renderers and the pickers
        sel = self.hidden_state['bonds'].invert().indices
        system = self.system
        
        # We need to update the pickers...
        self.bond_picker = CylinderPicker(
            self.viewer.widget,
            system.r_array.take(self.system.bonds, axis=0)[sel, :],
            self.bond_radii[sel])
        
        # And the bond renderer
        self.viewer.remove_renderer(self.bond_renderer)
        self.bond_renderer = self.viewer.add_renderer(BondRenderer,
                                                      system.bonds[sel], system.r_array,
                                                      system.type_array, style='impostors')
        
        self.viewer.update()

    def on_atom_selection_changed(self):
        #self.glow_timer.stop()
        # When selection state changes, the view update itself
        sel = self.selection_state['atoms'].indices
        cols = np.array(self.atom_colors.array)
        
        cols[sel, -1] = 50
                    
        self.atom_renderer.update_colors(cols)
        self.viewer.update()
    
    def on_bond_selection_changed(self):
        # When selection state changes, the view update itself
        if self.system.n_bonds == 0:
            return
        
        sel = self.selection_state['bonds'].indices
        cols_a, cols_b = self.bond_colors
        
        cols_a = cols_a.copy()
        cols_b = cols_b.copy()
        
        cols_a[sel, -1] = 50
        cols_b[sel, -1] = 50
        
        hmsk = self.hidden_state['bonds'].invert().indices
        self.bond_renderer.update_colors(cols_a[hmsk], cols_b[hmsk])

    def on_click(self, x, y):
        # This is basically our controller
        x, y = self.viewer.widget.screen_to_normalized(x, y)
        
        # I need another picker
        a_indices, a_dists = self.atom_picker.pick(x, y)
        b_indices, b_dists = self.bond_picker.pick(x, y)
        
        indices = list(itertools.chain(a_indices, b_indices))
        
        #print 'A', a_indices, a_dists
        #print 'B', b_indices, b_dists
        
        # This applies only to visible atoms
        
        visible_atoms = self.hidden_state['atoms'].invert().indices
        #visible_atoms = (~self.hidden_state.atom_hidden_mask).nonzero()[0]
        
        if len(indices) == 0 :
            # Cancel selection
            self.selection_state['atoms'] = Selection([], self.system.n_atoms)
            self.selection_state['bonds'] = Selection([], self.system.n_bonds)
            self.on_atom_selection_changed()
            self.on_bond_selection_changed()
        else:
            # Determine the candidate
            dist_a = a_dists[0] if a_indices else float('inf')
            dist_b = b_dists[0] if b_indices else float('inf')
            
            if dist_a < dist_b:
                self.atom_clicked.emit(visible_atoms[a_indices[0]])
                
                self.selection_state['atoms'] \
                    = self.selection_state['atoms'].subtract(
                        Selection([visible_atoms[a_indices[0]]],
                                  self.system.n_atoms))
                self.on_atom_selection_changed()
            else:
                # TODO: fix for visible bonds
                self.bond_clicked.emit([b_indices[0]])
                self.selection_state['bonds'] \
                    = self.selection_state['bonds'].subtract(
                        Selection([b_indices[0]], self.system.n_bonds))
                self.on_bond_selection_changed()
                
        self.viewer.widget.update()
        
    def select(self, selections):
        '''Make a selection in this
        representation. BallAndStickRenderer support selections of
        atoms and bonds.
        
        To select the first atom and the first bond you can use the
        following code::
        
            from chemlab.mviewer.state import Selection        
            representation.select({'atoms': Selection([0], system.n_atoms),
                                   'bonds': Selection([0], system.n_bonds)})

        Returns the current Selection
        '''
        if 'atoms' in selections:
            self.selection_state['atoms'] = selections['atoms']
            self.on_atom_selection_changed()

        if 'bonds' in selections:
            self.selection_state['bonds'] = selections['bonds']
            self.on_bond_selection_changed()

        if 'box' in selections:
            self.selection_state['box'] = selections['box']

        return self.selection_state

    def hide(self, selections):
        '''Hide objects in this representation. BallAndStickRepresentation
        support selections of atoms and bonds.

        To hide the first atom and the first bond you can use the
        following code::

            from chemlab.mviewer.state import Selection
            representation.hide({'atoms': Selection([0], system.n_atoms),
                                   'bonds': Selection([0], system.n_bonds)})

        Returns the current Selection of hidden atoms and bonds.

        '''
        if 'atoms' in selections:
            self.hidden_state['atoms'] = selections['atoms']
            self.on_atom_hidden_changed()

        if 'bonds' in selections:
            self.hidden_state['bonds'] = selections['bonds']
            self.on_bond_hidden_changed()

        if 'box' in selections:
            self.hidden_state['box'] = box_s = selections['box']
            if box_s.mask[0]:
                if self.viewer.has_renderer(self.box_renderer):
                    self.viewer.remove_renderer(self.box_renderer)
            else:
                if not self.viewer.has_renderer(self.box_renderer):
                    self.viewer.add_renderer(self.box_renderer)

        return self.hidden_state

    def scale(self, selections, factor):
        '''Scale the objects represented by *selections* up to a
        certain *factor*.

        '''
        if 'atoms' in selections:
            atms = selections['atoms'].mask
            if factor is None:
                    self.scale_factors[atms] = 1.0
            else:
                self.scale_factors[atms] = factor
    
        self.update_scale_factors(self.scale_factors)

    def change_radius(self, selections, value):
        '''Change the radius of each atom by a certain value
        
        '''
        if 'atoms' in selections:
            atms = selections['atoms'].mask
            if value is None:
                self.radii_state.array[atms] = [vdw_radii.get(t) * 0.3  for t in self.system.type_array[atms]]
            else:
                self.radii_state.array[atms] = value
    
        self.update_scale_factors(self.scale_factors)
            
    def change_color(self, selections, value):
        '''Change the color of each atom by a certain value. *value*
        should be a tuple.

        '''
        if 'atoms' in selections:
            atms = selections['atoms'].mask
            if value is None:
                #self.radii_state.array[atms] = [vdw_radii.get(t) * 0.3  for t in self.system.type_array[atms]]
                self.atom_colors.array[atms, 0:3] = [self.color_scheme.get(t, colors.deep_pink)[0:3]
                                                     for t in self.system.type_array[atms]]
            else:
                self.atom_colors.array[atms, 0:3] = value[0:3]
    
        self.atom_renderer.update_colors(self.atom_colors.array)
        self.on_atom_colors_changed()