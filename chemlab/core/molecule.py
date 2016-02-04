import numpy as np

from collections import Counter
from copy import copy

from .base import ChemicalEntity
from .attributes import Attribute, Relation, Field

from ..utils.formula import make_formula
from ..db import ChemlabDB
from ..libs.ckdtree import cKDTree
cdb = ChemlabDB()

masses = cdb.get("data", "massdict")

class Molecule(ChemicalEntity):
    __dimension__ = 'molecule'
    
    __attributes__ = {
        'r_array' : Attribute(shape=(3,), dtype='float', dim='atom', alias="coords"),
        'type_array' : Attribute(dtype='unicode', dim='atom'),
        'charge_array' : Attribute(dim='atom'),
        'bond_orders' : Attribute(dtype='int', dim='bond'),
        'atom_export' : Attribute(dtype=object, dim='atom'),
        'atom_name' : Attribute(dtype='unicode', dim='atom'),
        'residue_name' : Attribute(dtype='unicode', dim='atom'),
        'residue_id' : Attribute(dtype='uint8', dim='atom'),
    }
    __relations__ = {
        'bonds' : Relation(map='atom', shape=(2,), dim='bond')
    }
    __fields__ = {
        'molecule_name' : Field(dtype='unicode', alias='name'),
        'molecule_export': Field(dtype=object, alias='export')
    }
    
    def __init__(self, atoms, name=None, export=None, bonds=None):
        super(Molecule, self).__init__()
        self._from_entities(atoms, 'atom')
        if bonds:
            self.bonds = bonds
        
        if name:
            self.molecule_name = name
        
        self.export = export or {}
        self.molecule_name = make_formula(self.type_array)

    def __setattr__(self, name, value):
        if name == 'bonds': #TODO UGLY HACK
            bonds = self.get_attribute('bonds')
            if len(value) == 0:
                self.shrink_dimension(0, 'bond')
            elif bonds.size < len(value):
                self.expand_dimension(len(value), 'bond', relations={'bonds': value})
            elif bonds.size > len(value):
                self.shrink_dimension(len(value), 'bond')

        super(Molecule, self).__setattr__(name, value)
        
    @property
    def n_atoms(self):
        return self.dimensions['atom']

    @property
    def n_bonds(self):
        return self.dimensions['bond']
    
    def move_to(self, r):
        '''Translate the molecule to a new position *r*.
        '''
        dx = r - self.r_array[0]
        self.r_array += dx

# Those functions have a separate life
def guess_bonds(r_array, type_array):
    covalent_radii = cdb.get('data', 'covalentdict')
    MAXRADIUS = 0.3
    
    # Find all the pairs
    ck = cKDTree(r_array)
    pairs = ck.query_pairs(MAXRADIUS)
    
    bonds = []
    for i,j in pairs:
        threshold = 0.01
        a, b = covalent_radii[type_array[i]], covalent_radii[type_array[j]]
        rval = a + b
        

        thr_a = rval - threshold
        thr_b = rval + threshold 
        
        #thr_a2 = thr_a * thr_a
        thr_b2 = thr_b * thr_b
        dr2  = ((r_array[i] - r_array[j])**2).sum()
        
        if dr2 < thr_b2:
            bonds.append((i, j))
    return np.array(bonds)
    
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

    
