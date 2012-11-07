import numpy as np
from .molecule import Atom

# MAYBE: I think this thing would be just a test 
class MonatomicSystem(object):
    def __init__(self, atomlist, dimension):
        '''This system is made of all atoms of the same types'''
        
        self.atoms = atomlist
        self.boxsize = dimension
        self.n = len(self.atoms)
        self.type = atomlist[0].type
        self.rarray = np.array([a.coords for a in atomlist], dtype=np.float32)
        self.varray = np.array([[0.0, 0.0, 0.0] for atom in (atomlist)], dtype=np.float32)
        
    @classmethod
    def random(cls, type, number, dim=10.0):
        '''Return a random monatomic system made of *number* molecules
        fo type *type* arranged in a cube of dimension *dim* extending
        in the 3 directions.

        '''
        # create random in the range 0,1   dimension dim
        coords = np.random.rand(number, 3).astype(np.float32) * dim - dim/2
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

