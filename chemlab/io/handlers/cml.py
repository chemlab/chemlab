import numpy as np
from .base import IOHandler
from ...core import Molecule
import xml.etree.ElementTree as ET

class CmlIO(IOHandler):
    '''The CML format is described in http://www.xml-cml.org/.
    
    **Features**

    .. method:: read("molecule")
    
       Read the coordinates in a :py:class:`~chemlab.core.Molecule` instance.
       
    .. method:: write("molecule", mol)

       Writes a :py:class:`~chemlab.core.Molecule` instance in the CML format.
    '''
    
    can_read = ['molecule']
    can_write = ['molecule']
    
    def read(self, feature):
        self.check_feature(feature, "read")
        
        if feature == 'molecule':
            root = ET.fromstring(self.fd.read())            
            atom_array = root.find('atomArray')
            
            type_array = []
            r_array = []
            index_map = {}
            for i, at in enumerate(atom_array):
                
                x = at.attrib['x3']
                y = at.attrib['y3']
                z = at.attrib['z3']
                
                # Later used for bonds
                index_map[at.attrib['id']] = i
                
                type = at.attrib['elementType']
                r_array.append([float(x),float(y),float(z)])
                type_array.append(type)
            
            r_array = np.array(r_array)/10 # To nm
            type_array = np.array(type_array)
            
            bond_array = root.find('bondArray')
            bonds = []
            for bond in bond_array:
                a, b = bond.attrib['atomRefs2'].split()
                bonds.append((index_map[a], index_map[b]))
                
            bonds = np.array(bonds)
            return Molecule.from_arrays(r_array=r_array,
                                        type_array=type_array,
                                        bonds=bonds)
            
            
    def write(self, feature, mol):
        self.check_feature(feature, "write")
        
        lines = []
        if feature == 'molecule':
            
            x_mol = ET.Element('molecule')
            aa = ET.SubElement(x_mol, 'atomArray')
            for i in range(mol.n_atoms):
                at = ET.SubElement(aa, 'atom')
                x, y, z = mol.r_array[i] * 10
                at.attrib = dict(x3=str(x), y3=str(y), z3=str(z),
                                 id='a{}'.format(i),
                                 elementType=mol.type_array[i])

                
            bb = ET.SubElement(x_mol, 'bondArray')
                
            for b in mol.bonds:
                i, j = b
                bd = ET.SubElement(bb, 'bond')
                bd.attrib = dict(atomRefs2='a{}  a{}'.format(i, j),
                                 order='1')
                
            self.fd.write(str(ET.tostring(x_mol)))
    