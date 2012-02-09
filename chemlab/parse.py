#! /usr/bin/env python -tt

import re
import numpy as np
from numpy import linalg as LA


class Parsing:

    '''Parse the input file and generate a list of atoms and bonds instances'''    
    
    def __init__(self,file): 
    
        #a very big regex to parse and group the input file
        r = re.compile(('\s*(\d+)\s*(\w+)\s*(-?\d+\.\d+)\s*'
                        '\s*(-?\d+\.\d+)\s*(-?\d+\.\d+)\s*(\d+)\s*(.*)')) 
        
        f = open(file,'r')
        input = f.readlines()
        f.close()
        
        
        self.atoms=[]
        #BUILDING ATOM OBJECTS
        #generate a list of instances of Atom class
        for line in input:
            match=r.search(line)
            id=int(match.group(1))
            type=match.group(2)
            coords=[match.group(3),match.group(4),match.group(5)]
            coords = [float(s) for s in coords]
            self.atoms.append(Atom(id,type,coords))
        
        
        
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
    
    


