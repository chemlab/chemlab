'''Mol file handler'''
import numpy as np

from .base import IOHandler
from ...core import Molecule

class MolIO(IOHandler):
    '''Reader for MDL molfile
    http://en.wikipedia.org/wiki/Chemical_table_file. 
    
    **Features**

    .. method:: read("molecule")

        Read the molecule in a :py:class:`~chemlab.core.Molecule`
        instance.

    '''
    
    can_read = ['molecule']
    
    def read(self, feature):
        self.check_feature(feature, "read")
        
        if feature == 'molecule':
            string = open(self.filename).read()
            return parse_mol_string(string)
        
def parse_mol_string(string):
    lines = string.splitlines()
    # lines 0-2 are header/comments

    # line 3 is counting
    natoms = int(lines[3].split()[0])
    nbonds = int(lines[3].split()[1])
    
    coords = []
    types = []
    for i in range(natoms):
        at_fields = lines[i + 4].split()
        x, y, z, typ = at_fields[:4]
        coords.append([float(x), float(y), float(z)])
        types.append(typ)
    
    return Molecule.from_arrays(r_array = np.array(coords),
                                type_array = np.array(types))
        