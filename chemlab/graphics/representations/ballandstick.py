    
    
def _apply_selection(mask, selection, mode):
    # Apply a selection to a numpy mask using different modes
    if mode == 'exclusive':
        mask[...] = False
        mask[selection] = True
    elif mode == 'additive':
        mask[selection] = True
    elif mode == 'flip':
        mask[selection] = np.logical_not(mask[selection])
    else:
        raise ValueError('invalid mode: {}'.format(mode))

class SystemSelectionState(object):
    def __init__(self, self.system):
        self.atom_selection_mask = np.zeros(self.system.n_atoms, dtype='bool')
        self.bond_selection_mask = np.zeros(self.system.n_bonds, dtype='bool')

    def select_atoms(self, selection, mode='exclusive'):
        _apply_selection(self.atom_selection_mask, selection, mode)
        
    def select_bonds(self, selection, mode='exclusive'):
        _apply_selection(self.bond_selection_mask, selection, mode)

class SystemHiddenState(object):
    def __init__(self, system):
        self.atom_hidden_mask = np.zeros(self.system.n_atoms, dtype='bool')
        self.bond_hidden_mask = np.zeros(self.system.n_bonds, dtype='bool')

    def hide_atoms(self, selection, mode='exclusive'):
        _apply_selection(self.atom_hidden_mask, selection, mode)
    
    def hide_bonds(self, selection, mode='exclusive'):
        _apply_selection(self.bond_hidden_mask, selection, mode)


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
        self.cylinder_picker = CylinderPicker(self.viewer.widget, system.r_array,
                                              system.get_bond_array(), cylinder_radii)
        
    def highlight(self, indices):
        # Given the indices, we have to highlight the spheres
        pass
        
    def on_hidden_changed(self):
        # When hidden state changes, the view update itself
        pass
        
    def on_selection_changed(self):
        # When selection state changes, the view update itself
        pass
    
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