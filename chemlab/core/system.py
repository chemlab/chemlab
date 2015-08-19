import numpy as np
from .base import ChemicalEntity, Field, Attribute, Relation
 
class Atom(ChemicalEntity):
    __dimension__ = 'atom'
    __fields__ = {
        'r_array' : Field(alias='r', shape=(3,), dtype='float'),
        'type_array' : Field(dtype='S4'),
        'charge_array' : Field(dtype='float')
    }

    def __init__(self, type, r_array):
        super(Atom, self).__init__()
        self.r_array = r_array
        self.type_array = type

class Molecule(ChemicalEntity):
    __dimension__ = 'molecule'
    
    __attributes__ = {
        'r_array' : Attribute(shape=(3,), dtype='float', dim='atom'),
        'type_array' : Attribute(dtype='str', dim='atom'),
        'charge_array' : Attribute(dim='atom')
    }
    __relations__ = {
        'bonds' : Relation(map='atom', shape=(2,), dim='bond')
    }
    __fields__ = {
        'molecule_name' : Field(dtype='str'),
        'export': Field(dtype=object)
    }
    
    def __init__(self, atoms, export=None, bonds=None):
        super(Molecule, self).__init__()
        self._from_entities(atoms, 'atom')
        
        self.export = export
        self.bonds = bonds
        

class System(ChemicalEntity):
    __dimension__ = 'system'
    __attributes__ = {
        'r_array' : Attribute(shape=(3,), dtype='float', dim='atom'),
        'type_array' : Attribute(dtype='str', dim='atom'),
        'charge_array' : Attribute(dim='atom'),
        'molecule_name' : Attribute(dtype='str', dim='molecule')
    }
    
    __relations__ = {
        'bonds' : Relation(map='atom', shape=(2,), dim='bond'),
    }
    
    __fields__ = {
        'cell_lengths' : Field(dtype='float', shape=(3,))
    }
    
    def __init__(self, molecules=None):
        super(System, self).__init__()
        
        if molecules is None:
            molecules = []
        self.dimensions = {'molecule' : len(molecules),
                           'atom': sum(m.dimensions['atom'] for m in molecules),
                           'bond': sum(m.dimensions['bond'] for m in molecules)}
        
        if molecules:
            self._from_entities(molecules, 'molecule')

    
    @classmethod
    def empty(cls, molecule, atom):
        inst = super(System, cls).empty(atom=atom, molecule=molecule)
        return inst

    @property
    def n_mol(self):
        return self.dimensions['molecule']
    
    @property
    def n_atom(self):
        return self.dimensions['atom']

    # Old API
    @property
    def mol_indices(self):
        steps = np.ediff1d(self.maps['atom', 'molecule'].value)
        steps = np.insert(steps, 0, 1)
        return np.nonzero(steps)[0]
    
    @property
    def mol_n_atoms(self):
        idx = self.mol_indices
        idx = np.append(idx, len(self.maps['atom', 'molecule'].value))
        return np.ediff1d(idx)

    @property
    def molecules(self):
        return MoleculeGenerator(self)

    @property
    def atoms(self):
        return AtomGenerator(self)

    def get_molecule(self, index):
        return self.subentity(Molecule, index)
    
    def add(self, molecule):
        self.add_entity(molecule, Molecule)

class MoleculeGenerator(object):
    def __init__(self, system):
        self.system = system

    def __getitem__(self, key):
        if isinstance(key, slice):
            ind = range(*key.indices(self.system.n_mol))
            ret = []
            for i in ind:
                ret.append(self.system.get_molecule(i))

            return ret

        if isinstance(key, int):
            return self.system.get_molecule(key)


class AtomGenerator(object):
    def __init__(self, system):
        self.system = system

    def __getitem__(self, key):
        if isinstance(key, slice):
            ind = range(*key.indices(self.system.n_mol))
            ret = []
            for i in ind:
                ret.append(self.system.get_atom(i))

            return ret

        if isinstance(key, int):
            return self.system.get_atom(key)


def subsystem_from_molecules():
    pass

def subsystem_from_atoms():
    pass

def merge_systems():
    pass


if __name__ == '__main__':
    test_empty() 
