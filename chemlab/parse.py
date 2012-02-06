#! /usr/bin/env python -tt

import re
import numpy as np
from numpy import linalg as LA


class Parsing:

    '''Parse the input file and generate a list of atoms and bonds instances'''    
    
    def __init__(self,file): 
    
    #a very big regex to parse and group the input file
        r = re.compile(('(\s*\d+\s*)(\s*\w+\s*)(\s*[\-\s*]\d+\.\d+\s*)'
                        '(\s*[\-\s*]\d+\.\d+\s*)(\s*[\-\s*]\d+\.\d+\s*)(\s*\d+\s*)(.*)')) 
        
        f = open(file,'r')
        input = f.readlines()
        f.close()
        
        
        #BUILDING ATOM OBJECTS
        #generate a list of instances of Atom class
        self.atoms = [Atom(r.search(line).groups()) 
        for line in input if r.search(line)]
        
        
        #PARSING THE FILE TO GET THE COUPLES BONDED
        #initialize bonds' list and compile the regex for tha atom's id
        couples = []
        atom_id = re.compile('\s*(\d+)\s*')
        
        #looping the input's line
        for el in input:
            #match each line with the first big regex
            line = r.search(el)
            
            if line:
            
                #line.group(1) is the number of the current atom in 
                #the input line
                current_atom_id = line.group(1)
                
                #line.group(7) are the numbers of atoms which
                #the current one is bounded at
                bounded_atoms = line.group(7)
                
                #bounded_id.group(1) is one of the the bounded atom returned
                #by finditer()
                couples += [[int(current_atom_id),int(bounded_id.group(1))] 
                           for bounded_id in re.finditer(atom_id,bounded_atoms)
                           if int(current_atom_id) < int(bounded_id.group(1))]


        
        #BUILDING BOND OBJECTS
        self.bonds = []
        #looping over the couples previously determined
        for couple in couples:
            #looping over the atoms to match their id with the couple 
            for atom in self.atoms:
                if couple[0]==atom.id:
                    atom1 = atom
                if couple[1]==atom.id:
                    atom2 = atom
                    self.bonds += [Bond(atom1,atom2)]
                    break
        
        
    def build_molecule(self):
    
        return Molecule(self.atoms,self.bonds)
    
    

    def guess_molecule(self):
    
        return GuessedMolecule(self.atoms)



class GuessedMolecule:

    '''Guess the topology with some criteria'''
    
    def __init__(self,atoms):
    
        #binding atoms to the instance of the class and copying the list :-)
        self.atoms = atoms[:]
        #initializing bonds
        self.bonds = []
        
        #guessing bonds
        while atoms:
            atom1 = atoms.pop(0)
            for atom in atoms:
            
            #guessing C--H bonds
                if     (atom1.type=='C' and atom.type=='H' and
                       LA.norm(atom1.coordinates-atom.coordinates)<1.11):
                    self.bonds += [Bond(atom1,atom)]
            #guessing C--C bonds
                if     (atom1.type=='C' and atom.type=='C' and
                       LA.norm(atom1.coordinates-atom.coordinates)<1.6):
                    self.bonds += [Bond(atom1,atom)]


class Molecule:

    '''Building the molecule with atoms and bonds'''
    
    def __init__(self,atoms,bonds):
    
        #binding atoms to the instance of the class
        self.atoms = atoms
        #binding bonds to the instance of the class
        self.bonds = bonds
    
    
    
    
    
class Atom:
    '''Takes a line of the formatted input file.
    
    Build an atom with: 
    - id -> number in the input file
    - type -> type of atom we are dealing with for example C
    - coordinates -> a vector with the coordinates of the atom
    '''
    
    def __init__(self,args):
        
        #assign the id
        r = re.compile('\s*(\d+)\s*')
        self.id = int(r.search(args[0]).group(1))
        
        #assign the type
        r = re.compile('\s*(\w+)\s*')
        self.type = r.search(args[1]).group(1)
        
        #build a numpy array of coordiantes
        x = float(args[2])
        y = float(args[3])
        z = float(args[4])
        self.coordinates=np.array([x,y,z])
        
        


class Bond:

    '''Generate bond and bond properties '''
    
    def __init__(self,atom1,atom2):
    
        self.atom_bonded = [atom1.type,atom2.type]
        self.id_bonded = [atom1.id,atom2.id]
        self.lenght = LA.norm(atom1.coordinates - atom2.coordinates)
        
        
        
        


if __name__=='__main__':

    input=Parsing('tink.xyz')
    mol=input.guess_molecule()
    
    #atoms in the molecule are:
    print '\nATOMS IN THE MOLECULE'
    for atom in mol.atoms:
        print atom.id, atom.type, atom.coordinates
        
    #bonds per atom in the molecule
    print '\nBONDS IN THE MOLECULE'
    for bond in mol.bonds:
        print bond.atom_bonded