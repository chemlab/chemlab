import numpy as np
from ..db import ChemlabDB
cdb = ChemlabDB()


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
        at_indices = sys.mol_to_atom_indices(indices)
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


class BondsAttr(object):
    def __init__(self):
        self.name = 'bonds'
        self.fieldname = 'bonds'

    def from_array(self, sys, arr):
        if arr is None:
            self.on_empty(sys)
        else:
            sys.bonds = arr

    def assign(self, sys, arr):
        sys.bonds = arr

    def on_add_molecule(self, sys, mol):
        if sys.bonds.size == 0:
            sys.bonds = mol.bonds.copy()
        else:
            sys.bonds = np.concatenate((sys.bonds,
                                        mol.bonds.copy() + sys._at_counter))

    def on_get_molecule_entry(self, sys, index):
        bond_mask = np.zeros(sys.n_bonds, dtype='bool')
        for i, (s, e) in enumerate(sys.bonds):
            sel_ind_start = sys.mol_indices[index]
            sel_ind_end = sel_ind_start + sys.mol_n_atoms[index]

            is_start = (s >= sel_ind_start) & (s <= sel_ind_end)
            is_end = (e >= sel_ind_start) & (e <= sel_ind_end)

            bond_mask[i] = is_start and is_end

        return sys.bonds.take(bond_mask) - sys.mol_indices[index]

    def on_remove_molecules(self, sys, indices):
        # As usual, we should get the mapping from the old to the new
        # indices
        prev_indices = np.arange(sys.n_atoms, dtype='int')

        at_indices = sys.mol_to_atom_indices(indices)
        old_indices = np.delete(prev_indices, at_indices, axis=0)

        # Remove the bonds related to the removed atoms
        bond_mask = np.zeros(sys.n_bonds, 'bool')
        for ai in at_indices:
            has_bonds = (sys.bonds[:, 0] == ai) | (sys.bonds[:, 1] == ai)
            bond_mask |= has_bonds

        sys.bonds = sys.bonds[~bond_mask]

        # Now, readjust all the indices
        sys.bonds = -sys.bonds
        for i, j in enumerate(old_indices):
            sys.bonds[sys.bonds == -j] = i

    def on_empty(self, sys):
        # No idea how many bonds
        sys.bonds = np.zeros((0, 2), 'int')

    def on_reorder_molecules(self, sys, new_order):
        # old_atomic_indices
        old_ai = np.arange(sys.n_atoms, dtype='int')
        new_ai = np.empty(sys.n_atoms, 'int')

        # The size of the final arrays are the same, just overwrite
        # with the new order
        offset = 0
        for k, (o_i, o_n) in enumerate(zip(sys.mol_indices[new_order],
                                           sys.mol_n_atoms[new_order])):

            new_ai[offset: offset+o_n] = old_ai[o_i: o_i+o_n]

            offset += o_n

        # Replace the old atomic indices with the new ones

        # Nasty trick to ensure uniqueness
        sys.bonds = -sys.bonds
        for i, j in enumerate(new_ai):
            sys.bonds[sys.bonds == -i] = j

    def selection(self, sys, selection):
        # This is called when selecting some molecules
        # Special case
        if sys.bonds.size == 0:
            return sys.bonds

        # Select which bonds we have to take
        bond_mask = np.zeros(sys.n_bonds, 'bool')

        #sel_ind_start = sys.mol_indices[selection]
        #sel_ind_end = sel_ind_start + sys.mol_n_atoms[selection]

        # Reconstruct atom mask
        atom_indices = sys.mol_to_atom_indices(selection)
        mp = np.zeros(sys.n_atoms, 'bool')
        mp[atom_indices] = True

        # Now, see which bonds have their atoms selected , we have to
        # take this atoms and delete the others
        bond_mask_2d = mp.take(sys.bonds)
        bond_mask = bond_mask_2d[:, 0] & bond_mask_2d[:, 1]
        new_b = np.copy(sys.bonds[bond_mask])

        # We have to change to the new atomic indices
        old_ai = np.arange(sys.n_atoms, dtype='int')
        size = sum(sys.mol_n_atoms[selection])
        new_ai = np.empty(size, 'int')

        offset = 0
        for k, (o_i, o_n) in enumerate(zip(sys.mol_indices[selection],
                                           sys.mol_n_atoms[selection])):

            new_ai[offset: offset+o_n] = old_ai[o_i: o_i+o_n]
            offset += o_n

        # This maps the old indices to old indices in a fast way by
        # using numpy
        # http://stackoverflow.com/questions/3403973/f
        # ast-replacement-of-values-in-a-numpy-array
        index_map = new_ai
        mp = np.arange(sys.n_atoms)
        mp[index_map] = np.arange(index_map.size)
        new_b = mp.take(new_b)

        return new_b

    def concatenate(self, sys, othersys):
        # Need to add an offset when concatenating
        if sys.bonds.size == 0:
            return othersys.bonds + sys.n_atoms
        if othersys.bonds.size == 0:
            return sys.bonds.copy()
        else:
            return np.concatenate((sys.bonds, othersys.bonds + sys.n_atoms))

    def get(self, sys):
        return sys.bonds


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
