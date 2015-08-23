import numpy as np
from collections import Counter
from .base import ChemicalEntity, Field, Attribute, Relation, InstanceRelation
from .serialization import json_to_data, data_to_json

class Atom(ChemicalEntity):
    __dimension__ = 'atom'
    __fields__ = {
        'r_array' : Field(alias='r', shape=(3,), dtype='float'),
        'type_array' : Field(dtype='S4', alias='type'),
        'charge_array' : Field(dtype='float', alias='charge'),
        'atom_export' : Field(dtype=object, alias='export'),
    }

    def __init__(self, type, r_array, export=None):
        super(Atom, self).__init__()
        self.r_array = r_array
        self.type_array = type
        self.export = export or {}
    
    @classmethod
    def from_fields(cls, **kwargs):
        '''
        Create an `Atom` instance from a set of fields. This is a
        slightly faster way to initialize an Atom.
        
        **Example**

        >>> Atom.from_fields(type='Ar',
                             r_array=np.array([0.0, 0.0, 0.0]),
                             mass=39.948,
                             export={})
        '''
        obj = cls.__new__(cls)
        
        for name, field in obj.__fields__.items():
            if name in kwargs:
                field.value = kwargs[name]
        
        return obj

class Molecule(ChemicalEntity):
    __dimension__ = 'molecule'
    
    __attributes__ = {
        'r_array' : Attribute(shape=(3,), dtype='float', dim='atom'),
        'type_array' : Attribute(dtype='str', dim='atom'),
        'charge_array' : Attribute(dim='atom'),
        'bond_orders' : Attribute(dtype='int', dim='bond'),
        'atom_export' : Attribute(dtype=object, dim='atom')
    }
    __relations__ = {
        'bonds' : Relation(map='atom', shape=(2,), dim='bond')
    }
    __fields__ = {
        'molecule_name' : Field(dtype='str'),
        'molecule_export': Field(dtype=object, alias='export')
    }
    
    def __init__(self, atoms, export=None, bonds=None):
        super(Molecule, self).__init__()
        self._from_entities(atoms, 'atom')
        if bonds:
            self.bonds = bonds
        
        self.export = export or {}
        self.molecule_name = make_formula(self.type_array)

    def __setattr__(self, name, value):
        if name == 'bonds': #TODO UGLY HACK
            bonds = self.get_attribute('bonds')
            if bonds.size < len(value):
                self.expand_dimension(len(value), 'bond', relations={'bonds': value})
            elif bonds.size > len(value):
                print self.dimensions, len(value)
                self.shrink_dimension(len(value), 'bond')
            print self.dimensions
        super(Molecule, self).__setattr__(name, value)
        
    @property
    def n_atoms(self):
        return self.dimensions['atom']
    
    def move_to(self, r):
        '''Translate the molecule to a new position *r*.
        '''
        dx = r - self.r_array[0]
        self.r_array += dx

def make_formula(elements):
    c = Counter(elements)
    formula = ''
    if c["C"] != 0:
        formula += "C{}".format(c["C"])
        del c["C"]

    if c["H"] != 0:
        formula += "H{}".format(c["H"])
        del c["H"]

    for item, count in sorted(c.items()):
        if count ==1:
            formula += item
        else:
            formula += "{}{}".format(item, count)

    return formula

    

class System(ChemicalEntity):
    __dimension__ = 'system'
    __attributes__ = {
        'r_array' : Attribute(shape=(3,), dtype='float', dim='atom'),
        'type_array' : Attribute(dtype='str', dim='atom'),
        'charge_array' : Attribute(dim='atom'),
        'molecule_name' : Attribute(dtype='str', dim='molecule'),
        'bond_orders' : Attribute(dtype='int', dim='bond'),
        'atom_export' : Attribute(dtype=object, dim='atom'),
        'molecule_export' : Attribute(dtype=object, dim='molecule')
    }
    
    __relations__ = {
        'bonds' : Relation(map='atom', shape=(2,), dim='bond'),
    }
    
    __fields__ = {
        'cell_lengths' : Field(dtype='float', shape=(3,)),
        'box_vectors' : Field(dtype='float', shape=(3, 3))
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
    def empty(cls, **kwargs):
        """Create an empty, uninitialized System.
        
        **Example**
        ::
            System.empty(atom=9, molecule=3, bonds=6)
        
        """
        
        return super(System, cls).empty(**kwargs)

    @property
    def n_mol(self):
        return self.dimensions['molecule']
    
    @property
    def n_atoms(self):
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
    
    def _bonds_belongs_to(self, value):
        mbelong = self.maps['atom', 'molecule'].value.take(value)
        # Check if some bonds belong to cross-stuff
        if not ((mbelong - mbelong[:, 0, np.newaxis]) == 0).all():
            raise ValueError('Some bonds belong to more than one molecule')    
        return mbelong[:, 0]
        
    
    def __setattr__(self, name, value):
        # TODO: UGLY/HACK Retrocompatibility
        if name == 'bonds': #TODO UGLY HACK
            bonds = self.get_attribute('bonds')
            map_ = self.maps['bond', 'molecule']
            
            if bonds.size < len(value):
                # We have to infer for each bond which molecule it is
                belong = self._bonds_belongs_to(value)
                self.expand_dimension(len(value), 'bond', 
                                      relations={'bonds': value}, 
                                      maps={('bond', 'molecule') : belong.tolist()})
                
            elif bonds.size > len(value):
                belong = self._bonds_belongs_to(value)
                self.shrink_dimension(len(value), 'bond')
                self.maps['bond', 'molecule'].value = belong
        
        super(System, self).__setattr__(name, value)
    
    @classmethod
    def from_arrays(cls, **kwargs):
        '''Initialize a System from its constituent arrays. It is the
        fastest way to initialize a System, well suited for 
        reading one or more big System from data files.

        **Parameters**
        
        The following parameters are required:
        
        - type_array: An array of the types
        - maps: A dictionary that describes the relationships between 
                molecules in the system and atoms and bonds.
        
        **Example**
        
        This is how to initialize a System made of 3 water molecules::

                # Initialize the arrays that contain 9 atoms
                r_array = np.random.random((3, 9))
                type_array = ['O', 'H', 'H', 'O', 'H', 'H', 'O', 'H', 'H']
                
                # The maps tell us to which molecule each atom belongs to. In this 
                # example first 3 atoms belong to molecule 0, second 3 atoms
                # to molecule 1 and last 3 atoms to molecule 2.
                maps = {('atom', 'molecule') : [0, 0, 0, 1, 1, 1, 2, 2, 2]}
                System.from_arrays(r_array=r_array, 
                                   type_array=type_array,
                                   maps=maps)
                
                # You can also specify bonds, again with the its map that specifies
                # to to which molecule each bond belongs to.
                bonds = [[0, 1], [0, 2], [3, 4], [3, 5], [6, 7], [6, 8]]
                maps[('bond', 'molecule')] = [0, 0, 1, 1, 2, 2]
                System.from_arrays(r_array=r_array, 
                                   type_array=type_array,
                                   bonds=bonds,
                                   maps=maps)
                

        '''
        if 'mol_indices' in kwargs:
            raise DeprecationWarning('The mol_indices argument is deprecated, use maps instead. (See from_arrays docstring)')
        
        return super(System, cls).from_arrays(**kwargs)

    def get_molecule(self, index):
        return self.subentity(Molecule, index)
    
    def add(self, molecule):
        self.add_entity(molecule, Molecule)
    
    def reorder_molecules(self, new_order):
        """Reorder the molecules in the system according to
        *new_order*.

        **Parameters**

        new_order: np.ndarray((NMOL,), dtype=int)
            An array of integers
            containing the new order of the system.

        """
        self.reorder_dimension(new_order, 'molecule')
    
    def remove_atoms(self, indices):
        """Remove the atoms positioned at *indices*. The molecule
        containing the atom is removed as well.

        If you have a system of 10 water molecules (and 30 atoms), if
        you remove the atoms at indices 0, 1 and 29 you will remove
        the first and last water molecules.

        **Parameters**

        indices: np.ndarray((N,), dtype=int)
            Array of integers between 0 and System.n_atoms

        """
        mol_indices = self.atom_to_molecule_indices(indices)
        self.copy_from(self.where(molecule_index=mol_indices))

    def atom_to_molecule_indices(self, selection):
        '''Given the indices over atoms, return the indices over
        molecules. If an atom is selected, all the containing molecule
        is selected too.

        **Parameters**

        selection: np.ndarray((N,), dtype=int) | np.ndarray((NATOMS,), dtype=book)
             Either an index array or a boolean selection array over the atoms

        **Returns**

        np.ndarray((N,), dtype=int) an array of molecular indices.

        '''
        return np.unique(self.maps['atom', 'molecule'].value[selection])

    def where(self, **kwargs):
        """Return a subsystem where the conditions are met"""
        
        for stmt, arg in kwargs.items():
            if stmt is 'molecule_index':
                return self.sub_dimension(arg, 'molecule')
            if stmt is 'atom_index':
                return self.sub_dimension(arg, 'atom')

    def sort(self):
        self.reorder_dimension(np.argsort(self.molecule_name), 'molecule')


# TODO: deprecated
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


def subsystem_from_molecules(orig, selection):
    '''Create a system from the *orig* system by picking the molecules
    specified in *selection*.

    **Parameters**

    orig: System
        The system from where to extract the subsystem
    selection: np.ndarray of int or np.ndarray(N) of bool
        *selection* can be either a list of molecular indices to
        select or a boolean array whose elements are True in correspondence
        of the molecules to select (it is usually the result of a numpy
        comparison operation).
    
    **Example**

    In this example we can see how to select the molecules whose
    center of mass that is in the region of space x > 0.1::
    
        s = System(...) # It is a set of 10 water molecules
    
        select = []
        for i range(s.n_mol):
           if s.get_molecule(i).center_of_mass[0] > 0.1:
               select.append(i)
        
        subs = subsystem_from_molecules(s, np.ndarray(select)) 
    
    
    .. note:: The API for operating on molecules is not yet fully 
              developed. In the future there will be smarter
              ways to *filter* molecule attributes instead of
              looping and using System.get_molecule.
    
    '''
    return orig.where(molecule_index=selection)


def subsystem_from_atoms(orig, selection):
    '''Generate a subsystem containing the atoms specified by
    *selection*. If an atom belongs to a molecule, the whole molecule is
    selected.

    **Example**
    
    This function can be useful when selecting a part of a system
    based on positions. For example, in this snippet you can see
    how to select the part of the system (a set of molecules) whose
    x coordinates is bigger than 1.0 nm::
    
        s = System(...)
        subs = subsystem_from_atoms(s.r_array[0,:] > 1.0)
    
    **Parameters**

    orig: System
       Original system.
    selection: np.ndarray of int or np.ndarray(NA) of bool
       A boolean array that is True when the ith atom has to be selected or
       a set of atomic indices to be included.

    Returns:

    A new System instance.

    '''
    return orig.where(atom_index=selection)

def merge_systems(sysa, sysb, bounding=0.2):
    '''Generate a system by merging *sysa* and *sysb*.

    Overlapping molecules are removed by cutting the molecules of
    *sysa* that have atoms near the atoms of *sysb*. The cutoff distance
    is defined by the *bounding* parameter.

    **Parameters**

    sysa: System
       First system
    sysb: System
       Second system
    bounding: float or False
       Extra space used when cutting molecules in *sysa* to make space
       for *sysb*. If it is False, no overlap handling will be performed.

    '''

    if bounding is not False:
        # Delete overlaps.
        if sysa.box_vectors is not None:
            periodicity = sysa.box_vectors.diagonal()
        else:
            periodicity = False

        p = overlapping_points(sysb.r_array, sysa.r_array,
                               cutoff=bounding, periodic=periodicity)

        sel = np.ones(len(sysa.r_array), dtype=np.bool)
        sel[p] = False

        # Rebuild sysa without water molecules
        sysa = subsystem_from_atoms(sysa, sel)
    
    sysres = System.empty(sysa.n_mol + sysb.n_mol, sysa.n_atoms + sysb.n_atoms)
    
    # Assign the attributes
    for attr in type(sysa).attributes:
        attr.assign(sysres,
                    attr.concatenate(sysa, sysb))
    
    # edit the mol_indices and n_mol
    offset = sysa.mol_indices[-1] + sysa.mol_n_atoms[-1]
    sysres.mol_indices[0:sysa.n_mol] = sysa.mol_indices.copy()
    sysres.mol_indices[sysa.n_mol:] = sysb.mol_indices.copy() + offset
    sysres.mol_n_atoms = np.concatenate([sysa.mol_n_atoms, sysb.mol_n_atoms])
    
    sysres.box_vectors = sysa.box_vectors
    
    return sysres


if __name__ == '__main__':
    test_empty() 
