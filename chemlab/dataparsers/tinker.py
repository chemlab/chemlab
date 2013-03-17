"""Parsers related to tinker file formats from Molden.

"""
import re
from .. import Molecule, Atom

class TinkerXyzDataParser(object):

    def __init__(self, filename):
        self.filename = filename
        
    def get_avail_properties(self):
        return ["geometry"]
    
    def get_property(self, prop):
        if prop == "geometry":
            return self._parse_geom()

    def _parse_geom(self):
                #a very big regex to parse and group the input file
        r = re.compile(('\s*(\d+)\s*(\w+)\s*(-?\d+\.\d+)\s*'
                        '\s*(-?\d+\.\d+)\s*(-?\d+\.\d+)\s*(\d+)\s*(.*)')) 
        
        f = open(self.filename,'r')
        input = f.readlines()
        input.pop(0) # Removing the first comment line
        f.close()
        
        
        atoms=[]
        #BUILDING ATOM OBJECTS
        #generate a list of instances of Atom class
        for i, line in enumerate(input):
            match=r.search(line)
            
            if not match:
                raise Exception("Error parsing line %d in file %s\n>>> %s"%(i, self.filename, line[:-1]))
            
            id=int(match.group(1))
            type=match.group(2)
            coords=[match.group(3),match.group(4),match.group(5)]
            coords = [float(s) for s in coords]
            atoms.append(Atom(type,coords, id))        
        
        
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
        bonds = []
        #looping over the couples previously determined
        for couple in couples:
            #looping over the atoms to match their id with the couple 
            for atom in atoms:
                if couple[0]==atom.id:
                    atom1 = atom
                if couple[1]==atom.id:
                    atom2 = atom
                    bonds += [Bond(atom1,atom2)]
                    break

        return Molecule(atoms, bonds)
