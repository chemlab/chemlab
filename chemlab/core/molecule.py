#! /usr/bin/env python -tt

import numpy as np
from collections import Counter
import numpy as np

from ..data import symbols
from ..data import masses

class Molecule(object):
    '''Data container used to represent Molecules, or more in general
    a list of one or more atoms. Molecule can be initialized by passing a
    list of atoms, the two data containers do not share data. Data is
    copied between the two.
    
    Attributes relative to the Molecule:
    export  : dict
    
    Attributes relative to the constituent Atoms:
    r_array : numpy.array[n_atoms,3] of float
    type_array: numpy.array[n_atoms] of str
    m_array: numpy.array[n_atoms] of int
    atom_export_array: numpy.array[n_atoms] of dict

    '''
    # Association between the Molecule array attribute and the atom one
    atom_array_map = {'r_array': ('r', np.float64),
                      'type_array': ('type', object),
                      'm_array': ('mass', np.float64),
                      'atom_export_array': ('export', object)}
    
    fields = ('export', 'formula')
    
    def __init__(self,atoms,bonds=None, export=None):
        self.n_atoms = len(atoms)
        
        for arr_name, (field_name, dtyp) in Molecule.atom_array_map.iteritems():
            setattr(self, arr_name,
                    np.array([getattr(a, field_name) for a in atoms], dtype=dtyp))
            # Example:
            # self.r_array = np.array([a.r for a in atoms], dtype=np.float64)
        
        # Extra data for exporting reasons
        if export:
            self.export = export
        else:
            self.export = {}
            
        
    @classmethod
    def from_arrays(cls, **kwargs):
        # Test for required fields:
        if set(('r_array', 'type_array')) <= set(kwargs):
            raise Exception('r_array and type_array are required arguments.')
        
        inst = cls.__new__(Molecule)

        for arr_name, (field_name, dtyp) in Molecule.atom_array_map.items():
            # Special cases
            if kwargs.get('m_array', None) == None:
                inst.m_array = np.array([masses.typetomass[t] for t in kwargs['type_array']])            
            else:
                setattr(inst, arr_name, kwargs[arr_name])
        
        for field in Molecule.fields.items():
            # Special cases
            if kwargs.get('export', None) == None:
                inst.export = {}
            else:
                setattr(inst, field, kwargs[field])

        inst.n_atoms = len(inst.r_array)
        
        return inst
        
    @property
    def mass(self):
        return self.m_array.sum()
    
    @property
    def center_of_mass(self):
        return ((self.m_array * self.r_array)/self.m_array.sum()).sum(axis=0)

    @property
    def geometric_center(self):
        return self.r_array.sum(axis=0)/len(self.r_array)
        
    def move_to(self, r):
        dx = r - self.r_array[0]
        self.r_array += dx
    
    def __repr__(self):
        return "molecule({})".format(self._det_formula())
    
    def copy(self):
        mol = Molecule([atom.copy() for atom in self.atoms],
                       [], export=self.export.copy())
        
        return mol
        
    def _det_formula(self):
        elements = self.type_array
        c = Counter(elements)
        formula = ''
        if c["C"] != 0:
            formula += "C{}".format(c["C"])
            del c["C"]
        
        if c["H"] != 0:
            formula += "H{}".format(c["H"])
            del c["H"]

        for item, count in sorted(c.items()):
            if count ==1:
                formula += item
            else:
                formula += "{}{}".format(item, count)
        
        return formula
    formula = property(_det_formula)

def make_formula(elements):
    c = Counter(elements)
    formula = ''
    if c["C"] != 0:
        formula += "C{}".format(c["C"])
        del c["C"]

    if c["H"] != 0:
        formula += "H{}".format(c["H"])
        del c["H"]

    for item, count in sorted(c.items()):
        if count ==1:
            formula += item
        else:
            formula += "{}{}".format(item, count)

    return formula

    
class Atom(object):
    '''Data container used to represent an Atom. It exposes different
    attributes useful in chemical applications.

    type  : str
    r     : numpy.array[3]
    export: dict
    mass  : int
    '''

    fields = ("type", "r", 'export', "mass")
    
    def __init__(self,type,coords, export=None):
        self.type = type
        self.r = np.array(coords, dtype=np.float32)
        
        # Extra data for exporting reasons
        if export:
            self.export = export
        else:
            self.export = {}

        self.atno = symbols.symbol_list.index(type.lower()) + 1
        self.mass = masses.typetomass[type]

    def copy(self):
        return Atom(self.type, np.copy(self.r), self.id, export=self.export.copy())

    def __repr__(self):
        return "atom({}{})".format(self.type, self.id)

