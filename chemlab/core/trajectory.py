"""Trajectory class for chemlab"""
import numpy as np

class Trajectory(object):
    
    def __init__(self, coords, t=None, boxes=None):
        self._data = {}
        self.nframes = len(coords)
        self._ignored = set(['_ignored']) | set(self.__dict__.keys())
         
        self.coords = coords
        self.t = t if t is not None else np.arange(0, self.nframes) 
        self.boxes = boxes if boxes is not None else [None] * self.nframes

    def __setitem__(self, name, value):
        setattr(self, name, value)
    
    def __getitem__(self, name):
        return getattr(self, name)
        
    def at(self, frame, attributes=None):
        return {k: self[k][frame] for k in set(self.__dict__.keys()) - self._ignored}
    
    def map(self, func, attributes=None):
        for i in range(self.nframes):
            if attributes is None:
                yield func({k: self[k][i] for k in set(self.__dict__.keys()) - self._ignored})
            if isinstance(attributes, str):
                yield func(self[attributes][i])
            if isinstance(attributes, list):
                yield func({a: self[a][i] for a in attrbutes})
