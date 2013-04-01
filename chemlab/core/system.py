import numpy as np
from .molecule import Atom, Molecule
from ..data import units, masses
from collections import namedtuple


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
    
AttrData = namedtuple('AttrData', ['name', 'type'])


class System(object):
    '''A data structure containing information of a set of *N* Molecules
    and *NA* Atoms.
       
    **Parameters**
    
    molecules: list of molecules
       Molecules that constitute the System. The data **gets copied**    
       to the System, subsequent changes to the Molecule are not
       reflected in the System.
    
    boxsize: float, optional
       The size of one side of a cubic box containing the system. Periodic boxes
       are common in molecular dynamics.
    
    box_vectors: np.ndarray((3,3), dtype=float), optional
       You can specify the periodic box of another shape by giving 3 box vectors
       instead.

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

    
    
    .. py:attribute:: boxsize, optional
    
       :type: float or None
    
       Defines the size of the periodic box. Boxes defined with
       boxsize are cubic. Changes in *boxsize* are reflected in
       box.
    
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
    
    molecule_inherited={'mol_export': AttrData(name='export', type=object)}
    
    atom_inherited={'r_array': AttrData(name='r_array', type=np.float),
                    'm_array': AttrData(name='m_array', type=np.float),
                    'type_array': AttrData(name='type_array', type=np.object),
                    'atom_export_array': AttrData(name='atom_export_array', type=np.object)}
    
    def __init__(self, molecules, boxsize=None, box_vectors=None):
        n_mol = len(molecules)
        n_atoms = sum(m.n_atoms for m in molecules)
    
        # Initialize an empty system and fill it with molecules
        self._setup_empty(n_mol, n_atoms, boxsize, box_vectors)
        
        for mol in molecules:
            self.add(mol)
        
    @classmethod
    def empty(cls, n_mol, n_atoms, boxsize=None, box_vectors=None):
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
        inst._setup_empty(n_mol, n_atoms, boxsize, box_vectors)
        return inst

    def _setup_empty(self, n_mol, n_atoms, boxsize, box_vectors):
        self.n_mol = n_mol
        self.n_atoms = n_atoms
        
        self._mol_counter = 0
        self._at_counter = 0

        self.molecules = MoleculeGenerator(self)
        self.atoms = AtomGenerator(self)
        
        # Setup boxsize
        if boxsize:
            self.boxsize = boxsize
        else:
            self.box_vectors = box_vectors
        
        # Initialize molecule arrays
        
        # Special arrays
        self.mol_indices = np.zeros((n_mol,), dtype=np.int)
        self.mol_n_atoms = np.zeros((n_mol,), dtype=np.int)
        
        cls = type(self)
        # Initializing derived array attributes
        for arr_name, field in cls.molecule_inherited.iteritems():
            setattr(self, arr_name, np.zeros((n_mol,), dtype=field.type))

        # Initialize derived atom arrays
        for arr_name, field in cls.atom_inherited.iteritems():
            # Special case
            if arr_name == 'r_array':
                val = np.zeros((n_atoms,3), dtype=field.type)
            else:
                val = np.zeros((n_atoms,), dtype=field.type)
            
            setattr(self, arr_name, val)

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
        inst = cls.__new__(System)
        
        required = ['type_array', 'r_array', 'mol_indices']
        for r in required:
            if r not in kwargs:
                raise Exception('%s is a required argument.'%r)
            
        if kwargs['r_array'].shape[1] != 3:
            raise Exception('r_array should be of shape (N, 3), now it is %s'
                            %str(kwargs['r_array'].shape))
        
        n_atoms = len(kwargs['type_array'])
        n_mol = len(kwargs['mol_indices'])
        
        if 'm_array' not in kwargs:
            kwargs['m_array'] = np.array([masses.typetomass[t]
                                          for t in kwargs['type_array']])
        
        if 'atom_export_array' not in kwargs:
            kwargs['atom_export_array'] = np.array([{} for i in range(n_atoms)])
            
        if 'mol_export' not in kwargs:
            kwargs['mol_export'] = np.array([{} for i in range(n_mol)])
            

        for arr_name, field in cls.atom_inherited.items():
            setattr(inst, arr_name, np.array(kwargs[arr_name]))
        
        for arr_name, field_name in cls.molecule_inherited.items():
            setattr(inst, arr_name, np.array(kwargs[arr_name]))
        
        # Special guys here
        inst.mol_indices = np.array(kwargs['mol_indices'])
        # Calculate n_atoms
        shifted_indices = np.append(inst.mol_indices[1:], n_atoms)
        inst.mol_n_atoms = shifted_indices - inst.mol_indices
        
        inst.boxsize = kwargs.get('boxsize', None)
        inst.box_vectors = np.array(kwargs.get('box_vectors', None))
        
        if inst.boxsize:
            inst.box_vectors = np.array([[inst.boxsize, 0, 0],
                                         [0, inst.boxsize, 0],
                                         [0, 0, inst.boxsize]])
        
        inst.n_mol = n_mol
        inst.n_atoms = n_atoms
        
        return inst
        
    @classmethod
    def molecule_map(cls):
        for arr_name, (field_name, dtyp) in System.molecule_inherited.iteritems():
            yield arr_name, field_name
    
    @classmethod
    def atom_map(cls):
        for arr_name, (field_name, dtyp) in System.atom_inherited.iteritems():
            yield arr_name, field_name

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
        
        # Setting molecule-wise attributes
        for arr_name, (field_name, dtyp) in System.molecule_inherited.iteritems():
            attr = getattr(self, arr_name)
            attr[mc] = getattr(mol, field_name)
        
        # Setting atom-wise attributes
        for arr_name, (field_name, dtyp) in System.atom_inherited.iteritems():
            attr = getattr(self, arr_name)
            attr[ac:ac+mol.n_atoms] = getattr(mol, field_name).copy()
        
        self._mol_counter += 1
        self._at_counter += mol.n_atoms
        return
    
    def remove_molecules(self, indices):
        
        # Molecule arrays
        for arr in System.molecule_inherited.keys():
            setattr(self,arr, np.delete(getattr(self, arr), indices, axis=0))
            
        # Atomic arrays
        at_indices = self.mol_to_atom_indices(indices)
        for arr in System.atom_inherited.keys():
            setattr(self, arr, np.delete(getattr(self, arr), at_indices, axis=0))
        
        # Now the hard part, change mol_indices and mol_n_atoms
        self.mol_n_atoms = np.delete(self.mol_n_atoms, indices)
        
        size = len(self.mol_n_atoms)
        self.mol_indices = np.zeros(size, dtype=int)
        for i,n in enumerate(self.mol_n_atoms[:-1]):
            self.mol_indices[i+1] = self.mol_indices[i] + self.mol_n_atoms[i]
        
        self.n_mol = len(self.mol_n_atoms)
        self.n_atoms = len(self.r_array)
        
    def mol_to_atom_indices(self, indices):
        '''Given the indices over molecules, return the indices over
        atoms.
        
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
        sorted_index = np.array(zip(*sorted_index)[0])

        old_indices = self.mol_indices.copy()
        old_n_atoms = self.mol_n_atoms.copy()

        # We have to shuffle everything regarding atoms
        
        old_atom_arrays = {} # Storing old-ordered coordinates etc...
        for arr_name, (field_name, dtyp) in System.atom_inherited.iteritems():
            attr = getattr(self, arr_name)
            old_atom_arrays[arr_name] = attr.copy()
        
        offset = 0
        for k,(o_i,o_n) in enumerate(zip(old_indices[sorted_index],
                                         old_n_atoms[sorted_index])):

            for arr_name, (field_name, dtyp) in System.atom_inherited.iteritems():
                attr = getattr(self, arr_name)
                attr[offset: offset+o_n] = old_atom_arrays[arr_name][o_i: o_i+o_n]

            self.mol_indices[k] = offset
            self.mol_n_atoms[k] = o_n
            offset += o_n

        # Setting molecule-wise attributes
        for arr_name, (field_name, dtyp) in System.molecule_inherited.iteritems():
            attr = getattr(self, arr_name)
            attr[:] = attr[sorted_index]

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

        for arr_name, (field_name, dtyp) in System.atom_inherited.iteritems():
            kwargs[arr_name] = getattr(self, arr_name)[start_index:end_index]

        for sys_field, (mol_field, dtyp) in Molecule.atom_inherited.items():
            kwargs[mol_field] = getattr(self, sys_field)[index]
        
        return Molecule.from_arrays(**kwargs)
        
    def get_atom(self, index):
        return Atom.from_fields(r=self.r_array[index], export=self.atom_export_array[index],
                                type=self.type_array[index], mass=self.m_array)
        
    @property
    def boxsize(self):
        return self._boxsize
    
    @boxsize.setter
    def boxsize(self, value):
        if value == None:
            self._boxsize = None
        else:
            self._boxsize = value
            self.box_vectors = np.array([[value, 0, 0],
                                         [0, value, 0],
                                         [0, 0, value]])
        
    def _get_start_end_index(self, i):
        start_index = self.mol_indices[i]
        end_index = start_index + self.mol_n_atoms[i]
        return start_index, end_index
        
        
        
def lattice(mol, size=1, density=1.0):
    '''Generate an FCC lattice with *body* as points of the
    lattice. *size* is the number of primitive cells per dimension
    (eg *size=2* is a 2x2x2 lattice, for a total of 8 primitive
    cells) and density is the required *density* required to
    calculate volume and unit cell vectors.

    '''
    nmol = 4*size**3
    nat = nmol * mol.n_atoms
    
    sys = System.empty(nmol, nat)

    cell = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.0],
                     [0.5, 0.0, 0.5], [0.0, 0.5, 0.5]])

    grams =  units.convert(mol.mass*len(cell)*size**3, 'amu', 'g')

    vol = grams/density
    vol = units.convert(vol, 'cm^3', 'nm^3')
    dim = vol**(1.0/3.0)
    celldim = dim/size
    sys.boxsize = celldim*size

    cells = [size, size, size]
    for x in range(cells[0]):
        for y in range(cells[1]):
            for z in range(cells[2]):
                for cord in cell:
                    dx = (cord + np.array([float(x), float(y), float(z)]))*celldim
                    mol.r_array += dx
                    mol.r_array -= sys.boxsize / 2.0
                    sys.add(mol)
                    mol.r_array += sys.boxsize / 2.0
                    mol.r_array -= dx
                    
    #sys.rarray -= sys.boxsize/2.0
    return sys



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
    
    offset = 0
    
    for k,(o_i,o_n) in enumerate(zip(orig.mol_indices[index],
                                     orig.mol_n_atoms[index])):

        for arr_name, (field_name, dtyp) in System.atom_inherited.iteritems():
            o_attr = getattr(orig, arr_name)
            attr = getattr(ret, arr_name)
            
            attr[offset: offset+o_n] = o_attr[o_i: o_i+o_n]

        ret.mol_indices[k] = offset
        ret.mol_n_atoms[k] = o_n
        offset += o_n

    # Setting molecule-wise attributes
    for arr_name, (field_name, dtyp) in System.molecule_inherited.iteritems():
        o_attr = getattr(orig, arr_name)
        attr = getattr(ret, arr_name)
        attr[:] = o_attr[index]

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
    
    
def merge_systems(sysa, sysb, bounding=0.0):
    '''Generate a system by overlapping *sysa* and *sysb*. Overlapping
    molecules are removed by cutting the molecules of *sysa* that are
    found inside the space defined by :py:attr:`sysb.box_vectors
    <chemlab.core.System.box_vectors>`.

    **Parameters**
    
    sysa: System
       First system
    sysb: System
       Second system
    bounding: float
       Extra space used when cutting molecules in *sysa* to make space
       for *sysb*.
    
    '''
    # Delete overlaps.
    minx, miny, minz = np.min(sysb.r_array[:, 0]), np.min(sysb.r_array[:, 1]), np.min(sysb.r_array[:, 2])
    maxx, maxy, maxz = np.max(sysb.r_array[:, 0]), np.max(sysb.r_array[:,1]), np.max(sysb.r_array[:,2])

    maxx += bounding
    maxy += bounding
    maxz += bounding
    
    minx -= bounding
    miny -= bounding
    minz -= bounding
    
    xmask = (minx < sysa.r_array[:,0]) & (sysa.r_array[:,0] < maxx) 
    ymask = (miny < sysa.r_array[:,1]) & (sysa.r_array[:,1] < maxy) 
    zmask = (minz < sysa.r_array[:,2]) & (sysa.r_array[:,2] < maxz) 
    
    # Rebuild sysa without water molecules
    sysa = subsystem_from_atoms(sysa, np.logical_not(xmask & ymask & zmask))
    
    sysres = System.empty(sysa.n_mol + sysb.n_mol, sysa.n_atoms + sysb.n_atoms)
    
    # each atom attribute
    for attr_name in System.atom_inherited.keys():
        val = np.concatenate([getattr(sysa, attr_name), getattr(sysb, attr_name)])
        setattr(sysres, attr_name, val)
    
    # each molecule attribute
    for attr_name in System.molecule_inherited.keys():
        val = np.concatenate([getattr(sysa, attr_name), getattr(sysb, attr_name)])
        setattr(sysres, attr_name, val)
    
    # edit the mol_indices and n_mol
    offset = sysa.mol_indices[-1] + sysa.mol_n_atoms[-1]
    sysres.mol_indices[0:sysa.n_mol] = sysa.mol_indices.copy()
    sysres.mol_indices[sysa.n_mol:] = sysb.mol_indices.copy() + offset
    sysres.mol_n_atoms = np.concatenate([sysa.mol_n_atoms, sysb.mol_n_atoms])

    
    sysres.box_vectors = sysa.box_vectors
    
    return sysres

    
