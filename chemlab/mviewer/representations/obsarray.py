import numpy as np
from ..events import BoundEvent

class obsarray(object):
    def __init__(self, arr):
        self._arr = arr
        self.changed = BoundEvent(self, 'changed')
        self._callbacks = {}
        
    def __setitem__(self, key, val):
        self._arr[key] = val
        self.changed.emit()    
        
    def __getitem__(self, key):
        return self._arr[key]
        
    def __getattribute__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            return object.__getattribute__(self._arr, key)

    def __setattr__(self, key, val):
        try:
            return object.__setattr__(self, key, val)
        except AttributeError:
            return object.__setattr__(self._arr, key, val)

    def __repr__(self):
        return repr(self._arr)

    def __str__(self):
        return str(self._arr)
