'''Local directory database
'''
import cPickle
import os
from .base import EntryNotFound

class LocalDB(object):
    def __init__(self, directory):
        self.directory = directory
        
    def get(self, entry, feature):
        if feature == "molecule":
            try:
                fd = open(os.path.join(self.directory, 
                                       "molecule", entry))
                
            except IOError:
                raise EntryNotFound()
                
            return cPickle.load(fd)
            