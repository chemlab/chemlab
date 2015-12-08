"""Handlers for GROMACS trajectories xtc and trr formats

"""
import itertools
import os
import shutil
import time

import h5py
import numpy as np

from ...core import Trajectory
from ...libs.pyxdr import XTCReader
from .base import IOHandler


class XtcIO(IOHandler):
    '''Reader for GROMACS XTC trajectories.
    
    **Features**

    .. method:: read("trajectory")
    
       Read the frames from the file and returns the trajectory as an
       array of times and an array of atomic positions::

           >>> times, positions = datafile('traj.xtc').read('trajectory')
           [t1, t2, t3], [pos1, pos2, ...]

       positions is a *list* of ``np.ndarray(n_atoms, 3)``.
    
    .. method:: read("boxes")
    
       After reading the "trajectory" feature you can call
       `read("boxes")` that will return a list of *box_vectors*
       correspoiding to each frame.

    '''
    can_read = ['trajectory']
    can_write = []
    
    def read(self, feature, **kwargs):
        t0 = time.time()
        
        if feature == 'trajectory':
            skipframes = kwargs.get("skip", None)
            rootdir = kwargs.get("rootdir", None)
            
            if rootdir is not None:
                p = os.path
                rootdir = p.join(p.dirname(p.abspath(self.fd.name)), rootdir)
            
            xtcreader = XTCReader(self.fd.name)
            
            if rootdir is not None and os.path.exists(rootdir):
                f = h5py.File(rootdir, mode='r')
                if f.attrs["timestamp"] >= os.path.getmtime(self.fd.name):
                    return Trajectory(f['coords'], f['times'], f['boxes'])
                else:
                    f.close()
            
    
            handler = _NumpyFrameHandler() if rootdir is None \
                       else _HDF5FrameHandler(rootdir, os.path.getmtime(self.fd.name))
            
            for i, frame in enumerate(xtcreader):
                if skipframes is None or i%skipframes == 0:
                    handler.handle_frame(i, frame)
            
            handler.handle_done(i)
            
            return Trajectory(handler.frames, handler.times, handler.boxes)

class _NumpyFrameHandler:
    
    def __init__(self):
        self.cursize = 0
        
    def handle_frame(self, i, frame):
        self.cursize += 1
        
        if i == 0:
            self.frames = np.empty((1,) + frame.coords.shape, dtype='float32')
            self.boxes = []
            self.times = []
        
        # Enlarge if necessary
        if self.cursize > self.frames.shape[0]:
            self.frames.resize((self.cursize * 2, ) + frame.coords.shape)
                                       
        self.frames[self.cursize - 1, :] = frame.coords
        self.boxes.append(frame.box)
        self.times.append(frame.time)
    
    def handle_done(self, i):
        
        # Trim the edge
        if self.frames.shape[0] != self.cursize:
            self.frames.resize((i + 1, self.frames.shape[1], self.frames.shape[2]))
        
        self.boxes = np.array(self.boxes)
        self.times = np.array(self.times)



class _HDF5FrameHandler:
    
    def __init__(self, rootdir, timestamp):
        self.f = h5py.File(rootdir, 'w')
        self.f.attrs['timestamp'] = timestamp
        self.rootdir = rootdir
        self.cursize = 0
        self.boxes = []
        self.times = []
        
    def handle_frame(self, i, frame):
        self.cursize += 1
        
        if i == 0:
            self.frames = self.f.create_dataset("coords", 
                                                shape=(1,) + frame.coords.shape,
                                                maxshape=(None, frame.coords.shape[0], 3),
                                                compression='lzf',
                                                shuffle=True,
                                                dtype="float32")
        # Enlarge if necessary
        if self.cursize > self.frames.shape[0]:
            self.frames.resize((self.cursize * 2,) + frame.coords.shape)
                                       
        self.frames[self.cursize - 1, :] = frame.coords
        self.boxes.append(frame.box)
        self.times.append(frame.time)
    
    def handle_done(self, i):
        if self.frames.shape[0] != self.cursize:
            self.frames.resize((i + 1, self.frames.shape[1], self.frames.shape[2]))
        
        self.boxes = self.f.create_dataset("boxes", data=self.boxes)
        self.times = self.f.create_dataset("times", data=self.times)
        self.f.close()
        self.f = h5py.File(self.rootdir, 'r')
        
        self.frames = self.f['coords']
        self.times = self.f['times']
        self.boxes = self.f['boxes']

    
class _BcolzFrameHandler:
    
    def __init__(self, rootdir, timestamp):
        # Clean rootdir
        if os.path.exists(rootdir):
            shutil.rmtree(rootdir)

        os.mkdir(rootdir)

        self.rootdir = rootdir
        self.timestamp = timestamp
    
    def handle_frame(self, i, frame):
        if i == 0:
            self.frames = bcolz.carray(np.zeros((0,) + frame.coords.shape, dtype="float32"),
                                 rootdir=os.path.join(self.rootdir, "coords"),
                                 mode='w')
            self.frames.attrs['timestamp'] = self.timestamp
            self.boxes = bcolz.carray(np.zeros((0,) + frame.box.shape, dtype="float32"),
                                 rootdir=os.path.join(self.rootdir, "boxes"),
                                 mode='w')
            self.times = []

        self.frames.append(frame.coords)
        self.boxes.append(frame.box)
        self.times.append(frame.time)
    
    def handle_done(self, i):
        self.times = bcolz.carray(self.times, dtype='float32', rootdir=os.path.join(self.rootdir, "times"))
