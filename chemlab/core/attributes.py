import numpy as np
from ..db import cdb


class ArrayAttr(object):
    def __init__(self, name, fieldname, dtype, default=None):
        self.name = name
        self.dtype = dtype
        self.default = default
        self.fieldname = fieldname
    
    def from_array(self, sys, arr):
        if arr == None:
            if self.default is not None:
                setattr(sys, self.name, self.default(sys))
            elif self.default is False:
                raise Exception("array {} is required".format(self.name))
            else:
                self.on_empty(sys)
        else:
            setattr(sys, self.name, np.array(arr))

    def assign(self, sys, arr):
        getattr(sys, self.name)[:] = arr

    def get(self, sys):
        return getattr(sys, self.name)

    def concatenate(self, sys, othersys):
        return np.concatenate([self.get(sys), self.get(othersys)])
        
    def empty(self, sys, size):
        raise NotImplementedError()

    def on_empty(self, sys, size):
        raise NotImplementedError()

    def on_add_molecule(self, sys, mol):
        raise NotImplementedError()
        
    def on_get_molecule_entry(self, sys, index):
        raise NotImplementedError()
    
    def on_remove_molecule(self, sys, index):
        raise NotImplementedError()

    def on_reorder_molecules(self, sys, new_order):
        raise NotImplementedError()

    def selection(self, sys, selection):
        raise NotImplementedError()
        
class AtomicArrayAttr(ArrayAttr):

    def empty(self, sys, size):
        return np.zeros(size, dtype=self.dtype)
        
    def on_empty(self, sys):
        size = sys.n_atoms
        setattr(sys, self.name, self.empty(sys, size))
        
    def on_add_molecule(self, sys, mol):
        ac = sys._at_counter
        attr = getattr(sys, self.name)
        attr[ac:ac+mol.n_atoms] = getattr(mol, self.fieldname).copy()
        
    def on_remove_molecules(self, sys, indices):
        at_indices = self.mol_to_atom_indices(indices)
        setattr(sys, self.name, np.delete(getattr(sys, self.name), at_indices, axis=0))
    
    def on_reorder_molecules(self, sys, new_order):
        # Take a copy of the old array
        old_array = getattr(sys, self.name).copy()
        
        # The size of the final arrays are the same, just overwrite
        # with the new order
        offset = 0
        for k,(o_i,o_n) in enumerate(zip(sys.mol_indices[new_order],
                                         sys.mol_n_atoms[new_order])):

            attr = getattr(sys, self.name)
            attr[offset: offset+o_n] = old_array[o_i: o_i+o_n]

            offset += o_n
    
    def on_get_molecule_entry(self, sys, index):
        start_index, end_index = sys._get_start_end_index(index)
        return getattr(sys, self.name)[start_index:end_index]
    
    def selection(self, sys, selection):
        size = np.sum(sys.mol_n_atoms[selection])
        attr = self.empty(sys, size)
        o_attr = getattr(sys, self.name)
        
        offset = 0
        for k,(o_i,o_n) in enumerate(zip(sys.mol_indices[selection],
                                         sys.mol_n_atoms[selection])):
            attr[offset: offset+o_n] = o_attr[o_i: o_i+o_n]
            offset += o_n
        
        return attr

class MoleculeArrayAttr(ArrayAttr):

    def empty(self, sys, size):
        return np.zeros(size, dtype=self.dtype)
    
    def on_empty(self, sys):
        size = sys.n_mol
        setattr(sys, self.name, self.empty(sys, size))
    
    def on_add_molecule(self, sys, mol):
        mc = sys._mol_counter
        attr = getattr(sys, self.name)
        attr[mc] = getattr(mol, self.fieldname)
        
    def on_remove_molecules(self, sys, indices):    
        setattr(sys, self.name, np.delete(getattr(sys, self.name), indices, axis=0))
    
    def on_reorder_molecules(self, sys, new_order):
        attr = getattr(sys, self.name)
        attr[:] = attr[new_order]

    def on_get_molecule_entry(self, sys, index):
        return getattr(sys, self.name)[index]

    def selection(self, sys, selection):
        o_attr = getattr(sys, self.name)
        return o_attr[selection]

class MoleculeListAttr(MoleculeArrayAttr):
    def empty(self, sys, size):
        return [[] for i in range(size)]
    
    def on_reorder_molecules(self, sys, new_order):
        attr = getattr(sys, self.name)
        attr[:] = [attr[i] for i in new_order]

    def selection(self, sys, selection):
        o_attr = getattr(sys, self.name)
        return [o_attr[i] for i in selection]

    def from_array(self, sys, arr):
        if arr == None:
            if self.default is not None:
                setattr(sys, self.name, self.default(sys))
            elif self.default is False:
                raise Exception("array {} is required".format(self.name))
            else:
                self.on_empty(sys)
        else:
            setattr(sys, self.name, arr)

    def concatenate(self, sys, othersys):
        return self.get(sys) + self.get(othersys)
        
class NDArrayAttr(AtomicArrayAttr):
    
    def __init__(self, name, fieldname, dtype, ndim, default=None):
        super(NDArrayAttr, self).__init__(name, fieldname, dtype, default)
        self.ndim = ndim

    def empty(self, sys, size):
        return np.zeros((size, self.ndim), dtype=np.float)


class MArrayAttr(object):
    def __init__(self, name, fieldname, dtype, default=None):
        self.name = name
        self.dtype = dtype
        self.default = default
        self.fieldname = fieldname
        
    def get(self, at):
        return getattr(at, self.name)
        
    def set(self, at, value):
        setattr(at, self.name, value)

class MField(object):
    def __init__(self, name, dtype, default=None):
        self.name = name
        self.dtype = dtype
        self.default = default
        
    def get(self, at):
        return getattr(at, self.name)
        
    def set(self, at, value):
        setattr(at, self.name, value)