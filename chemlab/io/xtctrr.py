"""Handlers for GROMACS trajectories xtc and trr formats

"""
from .iohandler import IOHandler
import numpy as np

from pyxdr import XTCReader, TRRReader

class XtcIO(IOHandler):

    can_read = ['trajectory']
    can_write = []
    
    def __init__(self, filename):
        self.filename = filename
    
    def read(self, feature):
        if feature == 'trajectory':
            # TODO numpy array
            frames = []
    
            for frame in XTCReader(args.traj):
                frames.append(frame.coords)
                
            return frames
            
class TrrIO(IOHandler):
    
    can_read = ['trajectory']
    can_write = []
    
    def __init__(self, filename):
        self.filename = filename
    
    def read(self, feature):
        if feature == 'trajectory':
            # TODO numpy array
            frames = []
    
            for frame in TRRReader(args.traj):
                frames.append(frame.coords)
                
            return frames
    
    
        