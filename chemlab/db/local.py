'''Local directory database
'''
import numpy as np
import os
from .base import EntryNotFound, AbstractDB

class LocalDB(AbstractDB):
    '''Store serialized molecules and systems in a directory tree.
    
    See :ref:`localdb` for an example of usage.
    
    .. py:attribute:: directory

       Directory where the database is located.
    
    .. method:: get(self, 'molecule', key)

       Get an entry from the database. Key is the filename without
       extension of the serialized molecule. Molecules are stored in
       the subdirectory.
    
    .. method:: get(self, 'system', key)

       Get an entry from the database. Key is the filename without
       extension of the serialized system.

    .. method:: store(self, 'molecule', key, value)
    
    .. method:: store(self, 'system', key, value)

       Store a Molecule or a System passed as *value* in the directory
       structure. The objects are dumped to disk after being
       serialized to json.

    '''
    
    def __init__(self, directory):
        self.directory = directory
        
    def get(self, feature, key, *args, **kwargs):
        from ..core import Molecule, System
        
        if feature == "molecule":
            try:
                fd = open(os.path.join(self.directory, 
                                       "molecule", key+'.json'))
                
            except IOError:
                raise EntryNotFound(key + ' Not found')
                
            return Molecule.from_json(fd.read())

        elif feature == "system":
            try:
                fd = open(os.path.join(self.directory, 
                                       "system", key+'.json'))
                
            except IOError:
                raise EntryNotFound(key + ' Not found')
                
            return System.from_json(fd.read())
        else:
            raise Exception("Data type not present")
            
    def store(self, feature, key, value, nowarn=False):
        if feature == "molecule":
            destdir = "molecule"
        elif feature == "system":
            destdir = 'system'
        else:
            raise Exception("Data type not present")
        
        if not os.path.exists(os.path.join(self.directory, 
                                           destdir)):
            os.makedirs(os.path.join(self.directory, destdir))
        towrite = os.path.join(self.directory, destdir, key+'.json')
        if nowarn is not True:
            if os.path.exists(towrite):
                raise IOError("Database file {} exists".format(towrite))
                
        fd = open(towrite, 'w')
        
        fd.write(value.to_json())
