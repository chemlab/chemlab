import numpy as np
from .molecule import Atom
from ..data import units

# MAYBE: I think this thing would be just a test 
class MonatomicSystem(object):
    def __init__(self, atomlist, dimension):
        '''This system is made of all atoms of the same types'''
        
        self.atoms = atomlist
        self.boxsize = dimension
        self.n = len(self.atoms)
        self.type = atomlist[0].type
        self.rarray = np.array([a.coords for a in atomlist], dtype=np.float64)
        self.varray = np.array([[0.0, 0.0, 0.0] for atom in (atomlist)])
        
        
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
        
    def get_rarray(self):
        return self.__rarray
    
    def set_rarray(self, value):
        self.__rarray = value
        
        for i, atom in enumerate(self.atoms):
            atom.coords = self.__rarray[i]
    rarray = property(get_rarray, set_rarray)
    
    @classmethod
    def spaced_lattice(cls, type, number, dim=10.0):
        '''Return a spaced lattice in order to fill up the box with
        dimension *dim*

        '''
        n_rows = int(np.ceil(number**0.3333))
        
        step = dim/(n_rows+1)
        
        coords = []
        
        consumed = 0
        for i in range(1, n_rows+1):
            for j in range(1, n_rows+1):
                for k in range(1, n_rows+1):
                    consumed += 1
                    if consumed > number:
                        break
                    else:
                        c = np.array([step*i, step*j, step*k])-0.5*dim
                        # Introducing a small perturbation
                        c += (np.random.rand() - 0.5) * 0.1
                        coords.append(c)
        atoms = []
        
        for c in coords:
            atoms.append(Atom(type, c))
        
        return cls(atoms, dim)
        
        
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

    @property
    def n(self):
        return len(self.atoms)
        
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
                        sys.add(b)
        sys.rarray -= sys.boxsize/2.0
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
            self.rarray = np.concatenate((self.rarray, rar))
        
    def get_rarray(self):
        return self.__rarray
    
    def set_rarray(self, value):
        self.__rarray = value
        
        for i, atom in enumerate(self.atoms):
            atom.coords = self.__rarray[i]
    rarray = property(get_rarray, set_rarray)
    
    def __repr__(self):
        return "System(%d)"%self.n