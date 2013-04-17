'''Local directory database
'''
import cPickle
import numpy as np
import os
from .base import EntryNotFound

class LocalDB(object):
    def __init__(self, directory):
        self.directory = directory
        
    def get(self, entry, feature, *args, **kwargs):
        if feature == "molecule":
            try:
                fd = open(os.path.join(self.directory, 
                                       "molecule", entry))
                
            except IOError:
                raise EntryNotFound()
                
            return cPickle.load(fd)
        if feature == 'data':
            fd = open(os.path.join(self.directory,
                                   "data", "element.txt"))
                
            lines = fd.readlines()
            lines = [l for l in lines if not l.startswith('#')]
            fields = [l.split() for l in lines]

            if entry == 'vdwdict':
                vdw_tuples = [(f[1], float(f[5])/10) for f in fields]
                vdw_dict = dict(vdw_tuples)
                fd.close()
                return vdw_dict
            if entry == 'massdict':
                mass_tuples = [(f[1], float(f[5])/10) for f in fields]
                mass_dict = dict(mass_tuples)
                fd.close()
                return mass_dict
            
            if entry == 'symbols':
                return [f[1] for f in fields]