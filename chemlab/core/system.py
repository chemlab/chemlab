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


class SystemFast(object):
    molecule_inherited={'mol_export': AttrData(name='export', type=object),
                        'mol_formula': AttrData(name='formula', type=object)}
    
    atom_inherited={'r_array': AttrData(name='r_array', type=np.float),
                    'm_array': AttrData(name='m_array', type=np.float),
                    'type_array': AttrData(name='type_array', type=np.object),
                    'atom_export_array': AttrData(name='atom_export_array', type=np.object)}
    
    
    def __init__(self, n_mol, n_atoms, boxsize=None, box_vectors=None):
        # TODO set boxsize to False and do not display it
        if boxsize:
            self.boxsize = boxsize
        else:
            self.box_vectors = box_vectors
        
        self.n_mol = n_mol
        self.n_atoms = n_atoms
        
        self._mol_counter = 0
        self._at_counter = 0

        self.molecules = MoleculeGenerator(self)
        self.atoms = AtomGenerator(self)
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
        inst = cls.__new__(SystemFast)
        
        if kwargs.get('m_array', None) == None:
            inst.m_array = np.array([masses.typetomass[t] for t in kwargs['type_array']])
        else:
            inst.m_array = kwargs['m_array']

        special_cases = ['m_array']
        for arr_name, field in cls.atom_inherited.items():
            if arr_name in special_cases:
                continue
            setattr(inst, arr_name, kwargs[arr_name])
        
        for arr_name, field_name in cls.molecule_inherited.items():
            setattr(inst, arr_name, kwargs[arr_name])
        
        n_atoms = len(kwargs['r_array'])
        # Special guys here
        inst.mol_indices = kwargs['mol_indices']
        # Calculate n_atoms
        shifted_indices = np.append(inst.mol_indices[1:], n_atoms)
        inst.mol_n_atoms = shifted_indices - inst.mol_indices
        
        inst.boxsize = kwargs.get('boxsize', None)
        inst.box_vectors = kwargs.get('box_vectors', None)
        if inst.boxsize:
            inst.box_vectors = np.array([[inst.boxsize, 0, 0],
                                         [0, inst.boxsize, 0],
                                         [0, 0, inst.boxsize]])
        
        inst.n_mol = len(inst.mol_indices)
        inst.n_atoms = n_atoms
        
        return inst
        
    @classmethod
    def molecule_map(cls):
        for arr_name, (field_name, dtyp) in SystemFast.molecule_inherited.iteritems():
            yield arr_name, field_name
    
    @classmethod
    def atom_map(cls):
        for arr_name, (field_name, dtyp) in SystemFast.atom_inherited.iteritems():
            yield arr_name, field_name
            
    def add(self, mol):
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
        for arr_name, (field_name, dtyp) in SystemFast.molecule_inherited.iteritems():
            attr = getattr(self, arr_name)
            attr[mc] = getattr(mol, field_name)
        
        # Setting atom-wise attributes
        for arr_name, (field_name, dtyp) in SystemFast.atom_inherited.iteritems():
            attr = getattr(self, arr_name)
            attr[ac:ac+mol.n_atoms] = getattr(mol, field_name).copy()
        
        self._mol_counter += 1
        self._at_counter += mol.n_atoms
        return
    
    def remove_molecules(self, indices):
        
        # Molecule arrays
        for arr in SystemFast.molecule_inherited.keys():
            setattr(self,arr, np.delete(getattr(self, arr), indices, axis=0))
            
        # Atomic arrays
        at_indices = self.mol_to_atom_indices(indices)
        print at_indices
        for arr in SystemFast.atom_inherited.keys():
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
        sorted_index = sorted(enumerate(self.mol_formula),
                              key=lambda x: x[1])
        sorted_index = np.array(zip(*sorted_index)[0])

        old_indices = self.mol_indices.copy()
        old_n_atoms = self.mol_n_atoms.copy()

        # We have to shuffle everything regarding atoms
        
        old_atom_arrays = {} # Storing old-ordered coordinates etc...
        for arr_name, (field_name, dtyp) in SystemFast.atom_inherited.iteritems():
            attr = getattr(self, arr_name)
            old_atom_arrays[arr_name] = attr.copy()
        
        offset = 0
        for k,(o_i,o_n) in enumerate(zip(old_indices[sorted_index],
                                         old_n_atoms[sorted_index])):

            for arr_name, (field_name, dtyp) in SystemFast.atom_inherited.iteritems():
                attr = getattr(self, arr_name)
                attr[offset: offset+o_n] = old_atom_arrays[arr_name][o_i: o_i+o_n]

            self.mol_indices[k] = offset
            self.mol_n_atoms[k] = o_n
            offset += o_n

        # Setting molecule-wise attributes
        for arr_name, (field_name, dtyp) in SystemFast.molecule_inherited.iteritems():
            attr = getattr(self, arr_name)
            attr[:] = attr[sorted_index]

    def get_derived_molecule_array(self, attribute):
        arr = []
        for i in range(self.n_mol):
            arr.append(getattr(self.get_molecule(i), attribute))
        
        return np.array(arr)
        
    def get_molecule(self, index):
        start_index, end_index = self._get_start_end_index(index)
        
        kwargs = {}

        for arr_name, (field_name, dtyp) in SystemFast.atom_inherited.iteritems():
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
    
    sys = SystemFast(nmol, nat)

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
    
def select_atoms(sys, mask):
    '''Generate a subsystem containing the atoms specified by
    *mask*. If an atom belongs to a molecule, the molecules is also
    selected.
    
    Parameters:

    sys: System
       Origin system
    mask: list of True/False
       A mask to select certain atoms   

    '''
    # Which atom belongs to which molecule
    seq = np.array(range(sys.n_atoms))
    atomic_ids = seq[mask]
    molecule_ids = np.digitize(atomic_ids, sys.mol_indices)-1
    molecule_ids = np.unique(molecule_ids)

    return extract_subsystem(sys, molecule_ids)

def extract_subsystem(sys, index):
    '''Generate a system containing the molecules specifide by *indices*.

    Parameters:

    sys: System
        The system from where to extract the subsystem
    index: list of int
        A list of integers representing the molecules to pick.
    
    '''
    nmol = len(index)
    natom = np.sum(sys.mol_n_atoms[index])
    ret = SystemFast(nmol, natom)
    
    offset = 0
    for k,(o_i,o_n) in enumerate(zip(sys.mol_indices[index],
                                     sys.mol_n_atoms[index])):

        for arr_name, (field_name, dtyp) in SystemFast.atom_inherited.iteritems():
            o_attr = getattr(sys, arr_name)
            attr = getattr(ret, arr_name)

            attr[offset: offset+o_n] = o_attr[o_i: o_i+o_n]

        ret.mol_indices[k] = offset
        ret.mol_n_atoms[k] = o_n
        offset += o_n

    # Setting molecule-wise attributes
    for arr_name, (field_name, dtyp) in SystemFast.molecule_inherited.iteritems():
        o_attr = getattr(sys, arr_name)
        attr = getattr(ret, arr_name)
        attr[:] = o_attr[index]

    # Boxsize
    x = max(abs(ret.r_array[:,0]))
    y = max(abs(ret.r_array[:,1]))
    z = max(abs(ret.r_array[:,2]))
    
    ret.box_vectors = np.array([[x,0,0], [0,y,0], [0,0,z]])
    
    return ret

def merge_systems(sysa, sysb, bounding=0.2):
    '''Generate a system by overlapping *sysa* and *sysb*, overlapping
    molecules are removed, based on the size of the box.

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
    sysa = select_atoms(sysa, np.logical_not(xmask & ymask & zmask))
    
    sysres = SystemFast(sysa.n_mol + sysb.n_mol, sysa.n_atoms + sysb.n_atoms)
    
    # each atom attribute
    for attr_name in SystemFast.atom_inherited.keys():
        val = np.concatenate([getattr(sysa, attr_name), getattr(sysb, attr_name)])
        setattr(sysres, attr_name, val)
    
    # each molecule attribute
    for attr_name in SystemFast.molecule_inherited.keys():
        val = np.concatenate([getattr(sysa, attr_name), getattr(sysb, attr_name)])
        setattr(sysres, attr_name, val)
    
    # edit the mol_indices and n_mol
    offset = sysa.mol_indices[-1] + sysa.mol_n_atoms[-1]
    sysres.mol_indices[0:sysa.n_mol] = sysa.mol_indices.copy()
    sysres.mol_indices[sysa.n_mol:] = sysb.mol_indices.copy() + offset
    sysres.mol_n_atoms = np.concatenate([sysa.mol_n_atoms, sysb.mol_n_atoms])

    
    sysres.box_vectors = sysa.box_vectors
    
    return sysres

    
class System(object):
    def __init__(self, atomlist=None, boxsize=2.0):
        '''This system is made of all atoms of the same types'''
        
        if atomlist is None:
            atomlist = []
        
        self.atoms = atomlist

        self.boxsize = boxsize
        self.bodies = []
        
        
        self.rarray = np.array([a.coords for a in atomlist])
        self.varray = np.array([[0.0, 0.0, 0.0] for atom in (atomlist)])
        
        for atom in self.atoms:
            atom.system = self

    @property
    def n(self):
        return len(self.rarray)

    # Add body may be the same as add_molecule
    def add_body(self, body):
        # Should add each atom with its own coordinates
        
        # Should bind this guy's coordinates with my rarray
        
        pass
    
    @classmethod
    def random(cls, type, number, dim=10.0):
        '''Return a random monatomic system made of *number* molecules
        fo type *type* arranged in a cube of dimension *dim* extending
        in the 3 directions.

        '''
        # create random in the range 0,1   dimension dim
        coords = np.random.rand(number, 3) * dim - dim/2
        atoms = []
        for c in coords:
            atoms.append(Atom(type, c))
        
        return cls(atoms, dim)
        
    def random_add(self, body, min_distance=0.1, maxtries=1000):
        
        # try adding until you can 
        while maxtries:
            centers = []
            for b in self.bodies:
                centers.append(b.geometric_center)
            centers = np.array(centers)

            # Translate the molecule to its center of mass
            
            rar = body.rarray.copy()
            rar -= body.geometric_center
            
            # let's randomly rotate the molecule
            from ..graphics.gletools.transformations import random_rotation_matrix
            rar = np.dot(rar, random_rotation_matrix()[:3,:3].T)
            
            # randomly place the molecule
            mol_center = (np.random.rand(3) - 0.5) * self.boxsize
            rar += mol_center

            # if it's the only one molecule here it's ok
            if not self.bodies:
                body.rarray = rar
                self.bodies.append(body)
                self.atoms.extend(body.atoms)
                self.rarray = rar
                return
            
            # Minimum image convention for distance calculation
            dx = centers - mol_center
            minimage = abs(dx) > (self.boxsize*0.5)
            dx[minimage] -= np.sign(dx[minimage]) * self.boxsize
            distsq = (dx**2).sum(axis=1)
            
            if all(distsq > min_distance**2):
                # The guy is accepted
                body.rarray = rar
                self.bodies.append(body)
                self.atoms.extend(body.atoms)
                self.rarray = np.concatenate((self.rarray, rar))

                return
            else:
                maxtries -= 1

        raise Exception('Maximum tries for random insertion')
        
    @classmethod
    def lattice(cls, body, size=4, density=1.0):
        '''Generate an FCC lattice with *body* as points of the
        lattice. *size* is the number of primitive cells per dimension
        (eg *size=2* is a 2x2x2 lattice, for a total of 8 primitive
        cells) and density is the required *density* required to
        calculate volume and unit cell vectors.

        '''
        sys = cls()
        
        cell = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.0],
                         [0.5, 0.0, 0.5], [0.0, 0.5, 0.5]])

        grams =  units.convert(body.mass*len(cell)*size**3, 'amu', 'g')
        
        vol = grams/density
        vol = units.convert(vol, 'cm^3', 'nm^3')
        dim = vol**(1.0/3.0)
        celldim = dim/size
        sys.boxsize = dim
        
        cells = [size, size, size]
        for x in range(cells[0]):
            for y in range(cells[1]):
                for z in range(cells[2]):
                    for cord in cell:
                        b = body.copy()
                        b.rarray += (cord + np.array([float(x), float(y), float(z)]))*celldim
                        b.rarray -= sys.boxsize / 2.0
                        sys.add(b)
        #sys.rarray -= sys.boxsize/2.0
        return sys
        
    def add(self, body):
        rar = body.rarray
        if not self.bodies:
            self.bodies.append(body)
            self.atoms.extend(body.atoms)
            self.rarray = rar
        else:
            self.bodies.append(body)
            self.atoms.extend(body.atoms)
            self.__rarray = np.concatenate((self.rarray, rar))
        
        for atom in body.atoms:
            atom.system = self
        
    def replace(self, i, body):
        body = body.copy()
        
        # We have to update various things like atoms and rarray
        atoffset = roffset = self.atoms.index(self.bodies[i].atoms[0])

        
        replaced = self.bodies[i]
        pos = replaced.geometric_center
        body.rarray += pos
        
        self.atoms = (self.atoms[:atoffset] +
                      body.atoms +
                      self.atoms[atoffset+len(replaced.atoms):])
        
        self.rarray = np.concatenate([self.rarray[:roffset],
                                      body.rarray,
                                      self.rarray[roffset+len(replaced.rarray):]])
        
        self.bodies[i] = body
        for atom in body.atoms:
            atom.system = self
        
    def remove(self, i):
        atoffset = 0
        roffset = 0
        for j in range(i):
            bd = self.bodies[i]
            atoffset += len(bd.atoms)
            roffset += len(bd.rarray)
            
        replaced = self.bodies[i]
        
        self.atoms = (self.atoms[:atoffset] +
                      self.atoms[atoffset+len(replaced.atoms):])
        
        self.rarray = np.concatenate([self.rarray[:roffset],
                                      self.rarray[roffset+len(replaced.rarray):]])
        
        del self.bodies[i]
        
        
    def get_rarray(self):
        return self.__rarray
    
    def set_rarray(self, value):
        self.__rarray = value
        return
        for i, atom in enumerate(self.atoms):
            atom.coords = self.__rarray[i]
        
    rarray = property(get_rarray, set_rarray)
    
    def __repr__(self):
        return "System(%d)"%self.n
        
