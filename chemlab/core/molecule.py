#! /usr/bin/env python -tt

import re
import numpy as np
import os
import sys

from numpy import linalg as LA
from collections import Counter
import numpy as np

from .. import data
from ..data import symbols
from ..data import masses

class Molecule(object):
    '''Building the molecule with atoms and bonds'''
    
    def __init__(self,atoms,bonds=None, export=None):
    
        self.atoms=atoms
        
        self.rarray = np.array([a.coords for a in atoms], dtype=np.float64)
        self.marray = np.array([a.mass for a in atoms])
        
        if bonds != None:
            self.bonds=bonds
        else:
            self.guess_bonds()    
        
        # Extra data for exporting reasons
        if export:
            self.export = export
        else:
            self.export = {}
        
        self.det_angles()
        self.det_dihedrals()
        self._det_formula()
    
    @property
    def center_of_mass(self):
        return ((self.marray * self.rarray)/self.marray.sum()).sum(axis=0)

    @property
    def geometric_center(self):
        return self.rarray.sum(axis=0)/len(self.rarray)
        
    def __repr__(self):
        return "molecule({})".format(self.formula)
    
    def guess_bonds(self, threshold=0.1):
        d = os.path.dirname(sys.modules['chemlab.data'].__file__)
        
        radiifile = os.path.join(d, "covalent_radii.dat")
        radii = np.genfromtxt(radiifile,
                              delimiter=",",
                              dtype=[("type", "a3"),
                                     ("single", "f"),
                                     ("double", "f"),
                                     ("triple","f")])
        
        #initializing bonds
        self.bonds = []
        #copy to pop elements without damage
        atoms=self.atoms[:]
    
        #guessing bonds
        while atoms:
            atom1 = atoms.pop(0)
            for atom in atoms:
            
                cov_dist = (radii[atom1.atno-1][1] +
                            radii[atom.atno-1][1])

                cov_dist_inf = cov_dist - cov_dist * threshold
                cov_dist_sup = cov_dist + cov_dist * threshold
                
                if  (cov_dist_inf <
                     LA.norm(atom1.coords - atom.coords) <
                     cov_dist_sup):
                     self.bonds.append(Bond(atom1, atom))
    

    def copy(self):
        mol = Molecule([atom.copy() for atom in self.atoms],
                       [], export=self.export.copy())
        
        mol.bonds = []
        for bond in self.bonds:
            a1_id = bond.start.id
            a2_id = bond.end.id
            
            mol.bonds.append(Bond(mol.by_id(a1_id), mol.by_id(a2_id)))

        return mol
        

    def by_id(self, id):
        
        for atom in self.atoms:
            if atom.id == id:
                return atom
        
        raise Exception("No atom with such id: % d"%id)
        
    def det_angles(self):
        
        self.angles=[]
        bonds=self.bonds[:]
        
        while bonds:
            bond1 = bonds.pop(0)
            
            for bond2 in bonds:
                if bond1.start.id == bond2.start.id:
                    self.angles.append([bond2.end,bond2.start,bond1.end])
                if bond1.start.id == bond2.end.id:
                    self.angles.append([bond2.start,bond2.end,bond1.start])
                if bond1.end.id == bond2.start.id:
                    self.angles.append([bond1.start,bond1.end,bond2.end])
                if bond1.end.id == bond2.end.id:
                    self.angles.append([bond1.start,bond1.end,bond2.start])
                    
            
    
    def det_dihedrals(self):
    
        self.dihedrals=[]
        angles=self.angles[:]
        
        while angles:
            angle1 = angles.pop(0)
            
            for angle2 in angles:
                if    (angle1[1].id == angle2[0].id and 
                      angle1[2].id == angle2[1].id):
                    self.dihedrals.append([angle1[0],angle1[1],
                                           angle2[1],angle2[2]])        
    
    def _det_formula(self):
        elements = [a.type for a in self.atoms]
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
        
        self.formula = formula
        
class Atom:
    '''Takes a line of the formatted input file.
    
    Build an atom with: 
    - id -> number in the input file (if id is actually passed)
    - type -> type of atom we are dealing with for example C
    - coordinates -> a vector with the coordinates of the atom
    '''
    _curid = 0
    def __init__(self,type,coords, id=None, export=None):
        if id != None:
            self.id = id
        else:
            self.id = Atom._curid
            Atom._curid += 1
            
        self.type = type
        self.coords = np.array(coords, dtype=np.float32)
        
        # Extra data for exporting reasons
        if export:
            self.export = export
        else:
            self.export = {}


        self.atno = symbols.symbol_list.index(type.lower()) + 1
        self.mass = masses.typetomass[type]

    def copy(self):
        return Atom(self.type, np.copy(self.coords), self.id, export=self.export.copy())

    def __repr__(self):
        return "atom({}{})".format(self.type, self.id)

class Bond:

    '''Generate bond and bond properties '''
    
    def __init__(self,atom1,atom2):
    
        self.start = atom1
        self.end = atom2
        
        self.atom_bonded = [atom1.type,atom2.type]
        self.id_bonded = [atom1.id,atom2.id]
        self.lenght = LA.norm(atom1.coords - atom2.coords)

    def __repr__(self):
        return "bond({}{}, {}{})".format(self.start.id, self.start.type,
                                         self.end.id, self.end.type)
