'''Local directory database
'''
import numpy as np
import os
from .base import EntryNotFound

class LocalDB(object):
    def __init__(self, directory):
        self.directory = directory
        
    def get(self, feature, key, *args, **kwargs):
        if feature == "molecule":
            from ..core import Molecule
            try:
                fd = open(os.path.join(self.directory, 
                                       "molecule", key+'.json'))
                
            except IOError:
                raise EntryNotFound(key + ' Not found')
                
            return Molecule.from_json(fd.read())
            
