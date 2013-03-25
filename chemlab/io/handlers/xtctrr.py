"""Handlers for GROMACS trajectories xtc and trr formats

"""
from .base import IOHandler
import numpy as np
from ...libs.pyxdr import XTCReader


class BlockedArray(np.ndarray):
    def __init__(self, *args, **kwargs):
        super(BlockedArray, self).__init__(*args, **kwargs)
        self.block_size = 1000 # It preallocates 1000
        self._last_i = self.shape[0] - 1
        

    def append(self, item):
        assert item.shape == self.shape[1:]
        self._last_i += 1
        if self._last_i == self.shape[0]:
            self._enlarge()
        else:
            nslices = len(self.shape) - 1
            slices = (slice(None, None, None),)*nslices
            
            self[(self._last_i,)+slices] = item
        
        
    def _enlarge(self):
        newshape = list(self.shape)
        newshape[0] +=  self.block_size
        self.resize(newshape, refcheck=False)

    def trim(self):
        self.resize((self._last_i,) + self.shape[1:] , refcheck=False)
        
import itertools
class XtcIO(IOHandler):
    '''Reader for GROMACS XTC trajectories.
    
    **Features**

    .. method:: read("trajectory")
    
       Read the frames from the file and returns the trajectory as an
       array of times and an array of atomic positions::

           >>> times, positions = datafile('traj.xtc').read('trajectory')
           [t1, t2, t3], [pos1, pos2, ...]

       positions is a *list* of ``np.ndarray(n_atoms, 3)``.
    
       
    '''
    can_read = ['trajectory']
    can_write = []
    
    def __init__(self, filename):
        self.filename = filename
    
    def read(self, feature):
        import time
        t0 = time.time()
        
        if feature == 'trajectory':
            times = []
            xtcreader = XTCReader(self.filename)
            frames = []

            for frame in xtcreader:
                frames.append(frame.coords)
                times.append(frame.time)
            return times, frames
            
