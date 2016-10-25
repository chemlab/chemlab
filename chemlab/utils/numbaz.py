'''Numba utilities'''
from numba import jitclass
from numba.types import int32, boolean, float64
import numpy as np

spec = [
    ("size", int32),
    ("keys", int32[:]),
    ("values", float64[:]),
    ("occupied", boolean[:])
]

@jitclass(spec)
class Int32HashTable(object):

    def __init__(self, size):
        self.size = size
        self.keys = np.zeros(size, dtype=np.int32)
        self.values = np.zeros(size, dtype=np.float64)
        self.occupied = np.zeros(size, dtype=np.uint8)

    def map(self, keys):
        values = np.zeros_like(keys, dtype=np.int32)

        for i, k in enumerate(keys):
            values[i] = self.get(k)
            
        return values
    
    def get(self, key):
        return self.values[self.address(key)]

    def hash(self, key):
        return key
    
    def address(self, key):
        address = self.hash(key) % self.size

        while self.occupied[address] and self.keys[address] != key:
            address += 1
        
        return address

    def push(self, key, value):
        address = self.address(key)
        self.keys[address] = key
        self.values[address] = value
        self.occupied[address] = 1
