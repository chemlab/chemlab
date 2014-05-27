import numpy as np

from ..events import Model, Event
    
class Selection(object):
    def __init__(self, indices, total):
        '''A Selection is an object that keeps state of the selected
        status of a collection of entities, such as atoms or bonds.
        
        You don't instantiate them directly but they're tipically used
        by the other components.

        '''
        self.indices = indices
        self.total = total
        
        # Masks
        self.mask = np.zeros(self.total, dtype='bool')
        self.mask[self.indices] = True
        
    @classmethod
    def from_mask(cls, am):
        return Selection(indices=am.nonzero()[0], total=len(am))
    
    def add(self, other):
        am = self.mask | other.mask 
        
        return Selection.from_mask(am)

    def intersect(self, other):
        am = self.mask & other.mask 
        
        return Selection.from_mask(am)

    def subtract(self, other):
        am = np.logical_xor(self.mask, other.mask)

        return Selection.from_mask(am)

    def invert(self):
        am = np.logical_not(self.mask)

        return Selection.from_mask(am)

    def alltrue(self):
        return Selection.from_mask(np.ones_like(self.mask, 'bool'))

    def allfalse(self):
        return Selection.from_mask(np.zeros_like(self.mask, 'bool'))

    def __repr__(self):
        return 'Selection({})'.format(len(self.indices))

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

class ArrayState(Model):
    
    changed = Event()
    
    def __init__(self, default):
        super(ArrayState, self).__init__()
        self.default = default
        self.reset()

    @property
    def array(self):
        return self._array
        
    @array.setter
    def array(self, val):
        self._array = np.array(val)
    
    def reset(self):
        self.array = self.default
        
    def __setitem__(self, key, value):
        self.array[key] = value
        self.changed.emit()
        
        
