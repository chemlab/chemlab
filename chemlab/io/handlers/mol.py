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
            string = self.fd.read().decode('utf-8')
            return parse_mol_string(string)
        
def parse_mol_string(string):
    lines = string.splitlines()
    # lines 0-2 are header/comments

    # line 3 is counting
    natoms = int(lines[3][0:3])
    nbonds = int(lines[3][3:6])
    
    coords = []
    types = []
    bonds = []
    bond_types = []
    
    for i in range(natoms):
        at_fields = lines[i + 4].split()
        x, y, z, typ = at_fields[:4]
        coords.append([float(x), float(y), float(z)])
        types.append(typ)
    
    offset = natoms + 4
    for i in range(nbonds):
        s = lines[offset + i][0:3]
        e = lines[offset + i][3:6]
        t = lines[offset + i][6:9]
        bonds.append((int(s),int(e)))
        bond_types.append(int(t))
    
    mol = Molecule.from_arrays(r_array = np.array(coords)/10, # To nm
                               type_array = np.array(types), 
                               bonds=np.array(bonds) - 1)
    mol.bond_orders = np.array(bond_types)
    
    return mol
    
