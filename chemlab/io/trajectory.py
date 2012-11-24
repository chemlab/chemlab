import h5py
from chemlab.core.system import System
from chemlab.core.molecule import Atom

class Trajectory(object):
    def __init__(self, sys, filename, mode='w'):
        
        self.hdf = hd = h5py.File(filename, mode)

        if mode == 'w':
            #Variable length string
            str_type = h5py.new_vlen(str)
            tl =hd.create_dataset('types', (sys.n,), str_type)
            tl[:] = [at.type for at in sys.atoms]

            bsize = hd.create_dataset('boxsize', (1,), 'f')
            bsize[0] = sys.boxsize

            # The coordinate list
            cl = hd.create_dataset('coordlist', (1, sys.n, 3), 'f', maxshape=(None, sys.n, 3),
            compression='gzip', compression_opts=4)
            cl[0] = sys.rarray
            
            # The velocity list
            vl = hd.create_dataset('velocitylist', (1, sys.n, 3), 'f', maxshape=(None, sys.n, 3),
            compression='gzip', compression_opts=4)
            vl[0] = sys.varray


    @property
    def npoints(self):
        return self.hdf["coordlist"].shape[0]
        
    def _read_sys(self, index):
        atom_types = self.hdf["types"]
        coords = self.hdf["coordlist"][index]
        boxsize = self.hdf['boxsize'][0]
        
        return self._make_sys(atom_types, coords, boxsize)

    def _make_sys(self, atom_types, coords, boxsize):
        atlist = [Atom(typ, coord) for typ, coord in zip(atom_types, coords)]
        return System(atlist, boxsize)
        
    # Implementing list-like access
    def __getitem__(self, key):
        return self._make_sys(key)
    
    def last(self):
        return self[-1]

    def append(self, sys):
        clist = self.hdf["coordlist"]
        curi = clist.shape[0]
        
        # Resizing hdf data structure
        clist.resize((curi + 1, sys.n, 3))
        clist[curi] = sys.rarray

def make_trajectory(first, filename, restart=False):
    '''Factory function to easily create a trajectory object'''
    
    mode = 'w'
    if restart:
        mode = 'a'
    
    return Trajectory(first, filename, mode)
