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
    can_read = ['trajectory', 'boxes']
    can_write = []
    
    def read(self, feature, **kwargs):
        import time
        t0 = time.time()
        
        if feature == 'trajectory':
            skipframes = kwargs.get("skip", None)
            
            
            times = []
            xtcreader = XTCReader(self.fd.name)
            frames = []
            self._boxes = []

            for i, frame in enumerate(xtcreader):
                if skipframes is None or i%skipframes == 0:
                    frames.append(frame.coords)
                    times.append(frame.time)
                    self._boxes.append(frame.box)
                
            return times, frames
            
        if feature == 'boxes':
            return self._boxes