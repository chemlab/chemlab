#! /usr/bin/env python -tt

import re
import numpy as np
from numpy import linalg as LA



class Molecule:

    '''Building the molecule with atoms and bonds'''
    
    def __init__(self,atoms,bonds):
    
        self.atoms=atoms
        
        if bonds:
            self.bonds=bonds
        else:
            self.guess_bonds()    
    
    
    def guess_bonds(self):
        
        #initializing bonds
        self.bonds = []
        #copy to pop elements without damage
        atoms=self.atoms[:]
    
        #guessing bonds
        while atoms:
            atom1 = atoms.pop(0)
            for atom in atoms:
            
            #guessing C--H bonds
                if     (atom1.type=='C' and atom.type=='H' and
                       LA.norm(atom1.coords-atom.coords)<1.11):
                    self.bonds += [Bond(atom1,atom)]
            #guessing C--C bonds
                if     (atom1.type=='C' and atom.type=='C' and
                       LA.norm(atom1.coords-atom.coords)<1.6):
                    self.bonds += [Bond(atom1,atom)]
                    
                if      (atom1.type=='O' and atom.type=='H' and
                        LA.norm(atom1.coords-atom.coords)<10):
                    self.bonds += [Bond(atom1,atom)]
                
    
    
    
class Atom:
    '''Takes a line of the formatted input file.
    
    Build an atom with: 
    - id -> number in the input file (if id is actually passed)
    - type -> type of atom we are dealing with for example C
    - coordinates -> a vector with the coordinates of the atom
    '''
    
    def __init__(self,id,type,coords):
        
        self.id = id
        self.type = type
        self.coords = np.array(coords)
        
        


class Bond:

    '''Generate bond and bond properties '''
    
    def __init__(self,atom1,atom2):
    
        self.start = atom1
        self.end = atom2
        
        self.atom_bonded = [atom1.type,atom2.type]
        self.id_bonded = [atom1.id,atom2.id]
        self.lenght = LA.norm(atom1.coords - atom2.coords)
        