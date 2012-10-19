import numpy as np

# MAYBE: I think this thing would be just a test 
class MonatomicSystem:
    def __init__(self, atomlist):
        '''This system is made of all atoms of the same types'''
        
        self.atoms = atomlist
        
        self.rarray = np.array([a.coords for a in atomlist])
        self.varray = np.array([[0.0, 0.0, 0.0] for atom in (atomlist)])
    @classmethod
    def random(cls, number, dim=100.0):
        '''Return a random monatomic system made of *number* molecules
        arranged in a cube of dimension *dim* extending in the 3
        directions.

        '''
        pass
    
    @property
    def rarray(self):
        return self.__rarray
    
    @rarray.setter
    def rarray(self, rarray):
        # Every time we change this array we have to sync the Atom
        # objects
        self.__rarray = rarray
        for i, atom in enumerate(self.atoms):
            atom.coords = self.rarray[i]
