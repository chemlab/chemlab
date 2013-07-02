'''
chemlab.core.system
~~~~~~~~~~~~~~~~~~~

Creating and manipulating the System class.
'''
from collections import Counter

import numpy as np

from .molecule import Atom, Molecule, guess_bonds
from .attributes import (NDArrayAttr, AtomicArrayAttr, MoleculeArrayAttr,
                         BondsAttr)
from .serialization import json_to_data, data_to_json

from ..db import ChemlabDB
cdb = ChemlabDB()
masses = cdb.get("data", "massdict")

from ..utils import overlapping_points


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


class System(object):
    '''A data structure containing information of a set of *N* Molecules
    and *NA* Atoms.

    **Parameters**

    molecules: list of molecules
       Molecules that constitute the System. The data **gets copied**
       to the System, subsequent changes to the Molecule are not
       reflected in the System.

    box_vectors: np.ndarray((3,3), dtype=float), optional
       You can specify a periodic box of another shape by giving 3 box vectors.

    The System class has attributes derived both from the Molecule and
    the Atom class.

    .. py:attribute:: r_array

       :type: np.ndarray((NA, 3), dtype=float)
       :derived from: Atom

       Atomic coordinates.

    .. py:attribute:: m_array

       :type: np.ndarray(NA, dtype=float)
       :derived from: Atom

       Atomic masses.

    .. py:attribute:: type_array

       :type: np.ndarray(NA, dtype=object) *array of str*
       :derived from: Atom

       Array of  all the atomic symbols. It can be used to select
       certain atoms in a system.
    
    .. py:attribute:: charge_array

       :type: np.ndarray(N, dtype=float)
       :derived from: Atom
    
       Array of the charges present on the atoms.

       **Example**

       Suppose you have a box of water defined by the System *s*, to
       select all oxygen atoms you can use the numpy selection rules::

           >>> oxygens = s.type_array == 'O'
           # oxygens is an array of booleans of length NA where
           # each True corresponds to an oxygen atom i.e:
           # [True, False, False, True, False, False]

       You can use the *oxygen* array to access other properties::

           >>> o_coordinates = s.r_array[oxygens]
           >>> o_indices = np.arange(s.n_atoms)[oxygens]


    .. py:attribute:: bonds

       :type: np.ndarray((NBONDS, 2), dtype=int)
       :derived from: Molecule

       An array of 2d indices that specify the index of the bonded
       atoms.

    .. py:attribute:: atom_export_array

       :type: np.ndarray(NA, dtype=object) *array of dict*
       :derived from: Atom


    .. py:attribute:: mol_export

       :type: np.ndarray(N, dtype=object) *array of dict*
       :derived from: Molecule

       Export information relative to the molecule.

    .. py:attribute:: box_vectors

       :type: np.ndarray((3,3), dtype=float) or None

       Those are the three vectors that define of the periodic box of
       the system.

       **Example**

       To define an orthorombic box of size 3, 4, 5 nm::

           >>> np.array([[3.0, 0.0, 0.0],  # Vector a
                         [0.0, 4.0, 0.0],  # Vector b
                         [0.0, 0.0, 5.0]]) # Vector c

    .. py:attribute:: n_mol

       :type: int

       Number of molecules.

    .. py:attribute:: n_atoms

       :type: int

       Number of atoms.

    .. py:attribute:: mol_indices

       :type: np.ndarray(N, dtype=int)

       Gives the starting index for each molecule in the atomic
       arrays. For example, in a System comprised of 3 water
       molecules::

           >>> s.mol_indices
           [0, 3, 6]
           >>> s.type_array[0:3]
           ['O', 'H', 'H']

       This array is used internally to retrieve all the
       Molecule derived data. Do not modify unless you know what
       you're doing.

    .. py:attribute:: mol_n_atoms

       :type: np.ndarray(N, dtype=int)

       Contains the number of atoms present in each molecule

    '''
    attributes = [
        AtomicArrayAttr('type_array', 'type_array', np.object),
        NDArrayAttr('r_array', 'r_array', np.float, 3),
        AtomicArrayAttr('m_array', 'm_array',  np.float,
                        default=lambda s: np.array([masses[t] for t in s.type_array])),
        AtomicArrayAttr('charge_array', 'charge_array',  np.float,
                        default=lambda s: np.zeros(len(s.type_array), np.float)),
        AtomicArrayAttr('atom_export_array', 'atom_export_array', np.object,
            default=lambda s: np.array([{} for i in range(s.n_atoms)], dtype=np.object)),
        MoleculeArrayAttr('mol_export', 'export', np.object,
            default=lambda s: np.array([{} for i in range(s.n_mol)], dtype=np.object)),
        BondsAttr(),
    ]

    def __init__(self, molecules, box_vectors=None):
        n_mol = len(molecules)
        n_atoms = sum(m.n_atoms for m in molecules)

        # Initialize an empty system and fill it with molecules
        self._setup_empty(n_mol, n_atoms, box_vectors)

        for mol in molecules:
            self.add(mol)

    @classmethod
    def empty(cls, n_mol, n_atoms, box_vectors=None):
        '''Initialize an empty System containing *n_mol* Molecules and
        *n_atoms* Atoms. The molecules can be added by using the
        method :py:meth:`~chemlab.core.System.add`.

        **Example**

        How to initialize a system of 3 water molecules::

            s = System.empty(3, 9)
            for i in range(3):
                s.add(water)

        '''
        inst = cls.__new__(System)
        inst._setup_empty(n_mol, n_atoms, box_vectors)
        return inst

    @classmethod
    def from_json(cls, string):
        """Create a System instance from a json string. Such strings
        are produced from the method
        :py:meth:`chemlab.core.System.tojson`

        """

        kwargs = json_to_data(string)
        return cls.from_arrays(**kwargs)

    def tojson(self):
        '''Serialize a System instance using json.

        .. seealso:: :py:meth:`chemlab.core.System.from_json`

        '''
        return data_to_json(self.todict())
        
    def todict(self):
        mycls = type(self)
        #Used to convert stuff to another type
        kwargs = {}
        # Copy attributes
        for attr in mycls.attributes:
            kwargs[attr.name] = attr.get(self)
        
        # Copy special fields
        kwargs['mol_indices'] = self.mol_indices
        kwargs['mol_n_atoms'] = self.mol_n_atoms
        kwargs['box_vectors'] = self.box_vectors
        
        return kwargs
        
    def astype(self, cls):
        return cls.from_arrays(**self.todict())
        
    def _setup_empty(self, n_mol, n_atoms, box_vectors):
        self.n_mol = n_mol
        self.n_atoms = n_atoms

        # Special arrays
        self.mol_indices = np.zeros((n_mol,), dtype=np.int)
        self.mol_n_atoms = np.zeros((n_mol,), dtype=np.int)

        self._mol_counter = 0
        self._at_counter = 0

        self.molecules = MoleculeGenerator(self)
        self.atoms = AtomGenerator(self)
        
        self.box_vectors = box_vectors
        
        cls = type(self)
        
        # Initializing array attributes -- delegated to the ArrayAttr
        # classes
        for attr in cls.attributes:
            attr.on_empty(self)
        
    @classmethod
    def from_arrays(cls, **kwargs):
        '''Initialize a System from its constituent arrays. It is the
        fastest way to initialize a System, well suited for 
        reading one or more big System from data files.

        **Parameters**
        
        The following parameters are required:
        
        - r_array
        - type_array
        - mol_indices

        To further speed up the initialization process you optionally      
        pass the other derived arrays:

        - m_array
        - mol_n_atoms
        - atom_export_array
        - mol_export

        **Example**
        
        Our classic example of 3 water molecules::

                r_array = np.random.random((3, 9))
                type_array = ['O', 'H', 'H', 'O', 'H', 'H', 'O', 'H', 'H']
                mol_indices = [0, 3, 6]
                System.from_arrays(r_array=r_array, type_array=type_array,
                                   mol_indices=mol_indices)

        '''
        inst = cls.__new__(cls)
        
        if 'mol_indices' not in kwargs:
            raise Exception('mol_indices is a required argument.')
        
        if 'type_array' not in kwargs:
            raise Exception('mol_indices is a required argument.')
        
        n_atoms = len(kwargs['type_array'])
        n_mol = len(kwargs['mol_indices'])
        
        inst.n_mol = n_mol
        inst.n_atoms = n_atoms
        
        for attr in cls.attributes:
            attr.from_array(inst, kwargs.get(attr.name, None))
        
        # Special guys here
        inst.mol_indices = np.array(kwargs['mol_indices'])
        # Calculate n_atoms
        shifted_indices = np.append(inst.mol_indices[1:], n_atoms)
        inst.mol_n_atoms = shifted_indices - inst.mol_indices
        
        if 'boxsize' in kwargs:
            raise Exception('boxsize is deprecated')

        box_vectors = kwargs.get('box_vectors', None)

        if box_vectors is not None:
            inst.box_vectors = np.array(box_vectors)
        else:
            inst.box_vectors = None

        inst.molecules = MoleculeGenerator(inst)
        inst.atoms = AtomGenerator(inst)
        return inst

    def add(self, mol):
        '''Add the molecule *mol* to a System initialized through
         :py:meth:`System.empty <chemlab.core.System.empty>`.

        '''
        mc = self._mol_counter
        ac = self._at_counter
        
        if ac == self.n_atoms:
            raise Exception("No more space for further atoms")
        if mc == self.n_mol:
            raise Exception('No more space for further molecules')
        
        if mc == 0:
            self.mol_indices[0] = 0
            self.mol_n_atoms[0] = mol.n_atoms
        else:
            m_idx = self.mol_indices[mc-1] + self.mol_n_atoms[mc-1]
            self.mol_indices[mc] = m_idx
            self.mol_n_atoms[mc] = mol.n_atoms
        
        for attr in type(self).attributes:
            attr.on_add_molecule(self, mol)
        
        self._mol_counter += 1
        self._at_counter += mol.n_atoms
    
    def remove_molecules(self, indices):
        """Remove the molecules positioned at *indices*.

        For example, if you have a system comprised of 10 water
        molecules you can remove the first, fifth and nineth by using::

            system.remove_molecules([0, 4, 8])

        **Parameters**
        
        indices: np.ndarray((N,), dtype=int)
            Array of integers between 0 and System.n_mol

        """

        # Shift the arrays
        for attr in self.attributes:
            attr.on_remove_molecules(self, indices)

        # Now the hard part, change mol_indices and mol_n_atoms
        self.mol_n_atoms = np.delete(self.mol_n_atoms, indices)

        size = len(self.mol_n_atoms)
        self.mol_indices = np.zeros(size, dtype=int)
        for i, n in enumerate(self.mol_n_atoms[:-1]):
            self.mol_indices[i+1] = self.mol_indices[i] + self.mol_n_atoms[i]

        self.n_mol = len(self.mol_n_atoms)
        self.n_atoms = len(self.r_array)

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
        self.remove_molecules(mol_indices)

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
        # Which atom belongs to which molecule
        atomic_ids = _selection_to_index(selection)
        molecule_ids = np.digitize(atomic_ids, self.mol_indices)-1
        molecule_ids = np.unique(molecule_ids)
        return molecule_ids

    def mol_to_atom_indices(self, indices):
        '''Given the indices over molecules, return the indices over
        atoms.

        **Parameters**

        indices: np.ndarray((N,), dtype=int)
            Array of integers between 0 and System.n_mol

        **Returns**

        np.ndarray((N,), dtype=int) the indices of all the atoms
        belonging to the selected molecules.

        '''
        rng = np.arange(self.n_atoms)
        ind = []

        for i in indices:
            s = self.mol_indices[i]
            e = s + self.mol_n_atoms[i]
            ind.extend(rng[s:e])

        return np.array(ind).flatten()

    def walk(self):
        for i in range(self.n_mol):
            for j in range(self.mol_n_atoms[i]):
                yield i, j, self.mol_indices[i]+j

    def sort(self):
        '''
        Sort the molecules in the system according to their
        brute formula.

        '''
        # We do have to sort by formula
        mol_formula = self.get_derived_molecule_array('formula')
        sorted_index = sorted(enumerate(mol_formula),
                              key=lambda x: x[1])
        sorted_index = np.array(list(zip(*sorted_index))[0])

        self.reorder_molecules(sorted_index)

    def reorder_molecules(self, new_order):
        """Reorder the molecules in the system according to
        *new_order*.

        **Parameters**

        new_order: np.ndarray((NMOL,), dtype=int)
            An array of integers
            containing the new order of the system.

        """

        old_indices = self.mol_indices.copy()
        old_n_atoms = self.mol_n_atoms.copy()

        # Reorder the attributes
        for attr in self.attributes:
            attr.on_reorder_molecules(self, new_order)

        # Reorder the special arrays first
        offset = 0
        for k, (o_i, o_n) in enumerate(zip(old_indices[new_order],
                                           old_n_atoms[new_order])):
            self.mol_indices[k] = offset
            self.mol_n_atoms[k] = o_n
            offset += o_n

    def get_derived_molecule_array(self, attribute):
        arr = []
        for i in range(self.n_mol):
            arr.append(getattr(self.get_molecule(i), attribute))

        return np.array(arr)

    def get_molecule(self, index):
        '''Get the Molecule instance corresponding to the molecule at
        *index*.

        This method is useful to use Molecule properties that are
        generated each time, such as Molecule.formula and
        Molecule.center_of_mass

        '''
        start_index, end_index = self._get_start_end_index(index)
        
        kwargs = {}

        for attr in self.attributes:
            kwargs[attr.fieldname] = attr.on_get_molecule_entry(self, index)
        
        return Molecule.from_arrays(**kwargs)
        
    def guess_bonds(self):
        '''Guess the bonds between the molecules constituent of the system.
        
        '''
        # Can contain intermolecular bonds, we don't want that
        bonds = guess_bonds(self.r_array, self.type_array)
        
        # Cleaning -- as a requirement we want that the bond is
        # between the same molecule
        
        # We make a map atom-to-molecule
        mol_map = np.empty(self.n_atoms, dtype='int')


        for ind, (i, n)in enumerate(zip(self.mol_indices, self.mol_n_atoms)):
            mol_map[i:i + n] = ind
        
        bonds_mol = mol_map.take(bonds)
        bonds_mask = bonds_mol[:, 0] == bonds_mol [:, 1]
        
        self.bonds = bonds[bonds_mask]
        
    @property
    def n_bonds(self):
        return len(self.bonds)
        
    def get_atom(self, index):
        return Atom.from_fields(r=self.r_array[index], export=self.atom_export_array[index],
                                type=self.type_array[index], mass=self.m_array)
        
    def _get_start_end_index(self, i):
        start_index = self.mol_indices[i]
        end_index = start_index + self.mol_n_atoms[i]
        return start_index, end_index

    def __repr__(self):
        counts = Counter(self.type_array)
        composition = ','.join('{} {}'.format(sym, counts[sym])
                               for sym in sorted(counts))
        return 'system({})'.format(composition)
            
# Functions to operate on systems
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
    index = _selection_to_index(selection)

    nmol = len(index)
    natom = np.sum(orig.mol_n_atoms[index])
    ret = System.empty(nmol, natom)

    # Setting attributes
    for attr in orig.attributes:
        val = attr.selection(orig, index)
        attr.from_array(ret, val)  # assign ready-made array

    # Setting special arrays
    offset = 0
    for k, (o_i, o_n) in enumerate(zip(orig.mol_indices[index],
                                     orig.mol_n_atoms[index])):
        ret.mol_indices[k] = offset
        ret.mol_n_atoms[k] = o_n
        offset += o_n

    ret.box_vectors = orig.box_vectors

    return ret


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
    # Which atom belongs to which molecule
    atomic_ids = _selection_to_index(selection)

    molecule_ids = np.digitize(atomic_ids, orig.mol_indices)-1
    molecule_ids = np.unique(molecule_ids)

    return subsystem_from_molecules(orig, molecule_ids)


def _selection_to_index(selection):
    selection = np.array(selection)
    if selection.dtype == bool:
        index, = selection.nonzero()
    else:
        index = selection

    if len(index) == 0:
        raise Exception('The selection you performed is void.')
    return index


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
