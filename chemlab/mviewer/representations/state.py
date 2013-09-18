import numpy as np

from ..events import Model, Event
    
def _apply_selection(mask, selection, mode):
    # Apply a selection to a numpy mask using different modes
    # the selection is applied inplace.
    if mode == 'exclusive':
        mask[...] = False
        mask[selection] = True
    elif mode == 'additive':
        mask[selection] = True
    elif mode == 'flip':
        mask[selection] = np.logical_not(mask[selection])
    else:
        raise ValueError('invalid mode: {}'.format(mode))

class MaskState(Model):
    atom_mask_changed = Event()
    bond_mask_changed = Event()
        
class SystemSelectionState(MaskState):
    def __init__(self, system):
        super(SystemSelectionState, self).__init__()
        self.system = system
        
        self.atom_selection_mask = np.zeros(self.system.n_atoms, dtype='bool')
        self.bond_selection_mask = np.zeros(system.n_bonds, dtype='bool')

    def select_atoms(self, selection, mode='exclusive'):
        _apply_selection(self.atom_selection_mask, selection, mode)
        self.atom_mask_changed.emit()
        
    def select_bonds(self, selection, mode='exclusive'):
        _apply_selection(self.bond_selection_mask, selection, mode)
        self.bond_mask_changed.emit()

    @property
    def atom_selection(self):
        return self.atom_selection_mask.nonzero()[0]
    
    @property
    def bond_selection(self):
        return self.bond_selection_mask.nonzero()[0]

class SystemHiddenState(MaskState):
    def __init__(self, system):
        super(SystemHiddenState, self).__init__()

        self.system = system
        self.atom_hidden_mask = np.zeros(self.system.n_atoms, dtype='bool')
        self.bond_hidden_mask = np.zeros(system.n_bonds, dtype='bool')

    def hide_atoms(self, selection, mode='exclusive'):
        _apply_selection(self.atom_hidden_mask, selection, mode)
        self.atom_mask_changed.emit()
        
    def hide_bonds(self, selection, mode='exclusive'):
        _apply_selection(self.bond_hidden_mask, selection, mode)
        self.bond_mask_changed.emit()
