from ...core import Atom, Molecule, System
from .base import IOHandler
from itertools import groupby
import numpy as np
from ...db import ChemlabDB

cdb = ChemlabDB()

symbols = cdb.get("data", "symbols")
u_symbols = [s.upper() for s in symbols]

class PdbIO(IOHandler):
    '''Starting implementation of a PDB file parser.
    
    .. note::

        This handler was developed as an example. If you like to
        contribute by implementing it you can write an email to the
        `mailing list <mailto: python-chemlab@googlegroups.com>`_.
    
    **Features**

    .. method:: read("molecule")
    
       Read the pdb file as a huge Molecule.
    
    .. method:: read("system")
    
       Read the pdb file as a System, where each residue is 
       a molecule.

    '''
    
    can_read = ['molecule', 'system']
    can_write = []
    
    def __init__(self, fd):
        self.lines = [line.decode('utf-8') for line in fd.readlines()]

        self.atoms = []        
        self.atom_res = []
        
        for line in self.lines:
            self.handle_line(line)
        resname = None
        
        
    def read(self, feature):
        if feature == 'molecule':
            return self.get_molecule()
        if feature == 'system':
            return self.get_system()
            
    def handle_line(self, line):
        if line[0:6] == 'ATOM  ':
            self.handle_ATOM(line)
        if line[0:6] == 'HETATM':
            self.handle_ATOM(line)

    def handle_ATOM(self, line):
        serial = int(line[6:12])
        name = line[12:16]
        
        resname = line[17:20]
        x = float(line[31:38])
        y = float(line[39:46])
        z = float(line[47:54])
        
        # Standard residues just contain the following atoms
        # C, N, H, S and the first is the type
        
        # Normalized type        
        type = name[0:2].lstrip()
        i = u_symbols.index(type.upper())
        type = symbols[i]
        
        self.atom_res.append(resname)
        # Angstrom to nanometer
        self.atoms.append(Atom(type, [x/10.0, y/10.0, z/10.0]))
        
    def get_system(self):
        r_array = np.array([a.r for a in self.atoms])
        type_array = np.array([a.type for a in self.atoms])
        atom_export_array = np.array([a.export for a in self.atoms])
        mol_indices = []
        mol_names = []

        
        for key, group in groupby(enumerate(self.atom_res), lambda x: x[1]):
            group = iter(group)
            first_element = next(group)
            mol_indices.append(first_element[0])
            mol_names.append(first_element[1])
        
        mol_export = [{'pdb.residue': res} for res in mol_names]
            
        return System.from_arrays(r_array=r_array,
                                  type_array=type_array,
                                  mol_indices=mol_indices,
                                  atom_export_array=atom_export_array,
                                  mol_formula=mol_names,
                                  mol_export=mol_export)
    
    def get_molecule(self):
        m = Molecule(self.atoms)
        return m
        

