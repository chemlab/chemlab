from ...core import Atom, Molecule, System
from .base import IOHandler
from io import BytesIO
from itertools import groupby, count
import numpy as np
from ...db import ChemlabDB
import operator
import os
import re

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
        self.fd = fd

        # Fix for BytesIO which doesn't have 'mode'
        if isinstance(fd, BytesIO):
            if fd.tell() == 0:
                fd.mode = 'w'
            else:
                fd.mode = 'r'
            
        resname = None
        
    def read(self, feature):
        self.lines = [line.decode('utf-8') for line in self.fd.readlines()]
        self.atoms = []        
        self.atom_res = []
        self._res_ids = []
        # Holding info about beta sheets
        self._sheets = []
        self._helix = []
        self._is_amino = []
        
        self._box_vectors = None
        for line in self.lines:
            self.handle_line(line)
            
        self.set_header()
        self.set_title()
        self.set_expdta()
            
        if feature == 'molecule':
            return self.get_molecule()
        if feature == 'system':
            return self.get_system()
            
    def handle_line(self, line):
        if line[0:6] == 'ATOM  ':
            self.handle_ATOM(line)
        if line[0:6] == 'HETATM':
            self.handle_ATOM(line, False)
        if line[0:6] == 'CRYST1':
            self.handle_CRYST(line)
        if line[0:6] == 'SHEET ':
            self.handle_SHEET(line)
        if line[0:6] == 'HELIX ':
            self.handle_HELIX(line)

    def handle_ATOM(self, line, is_aminoacid=True):
        export = {}
        
        serial = int(line[6:12])
        name = line[12:16]
        
        resname = line[17:20]
        export['pdb.resname'] = resname
        
        x = float(line[31:38])
        y = float(line[39:46])
        z = float(line[47:54])
        
        # Standard residues just contain the following atoms
        # C, N, H, S and the first is the type
        type = name[0:2].lstrip()
        export['pdb.type'] = type

        # Normalized type                
        atom_type = line[76:78].lstrip()
        atom_type = symbols[u_symbols.index(atom_type.upper())]
        
        # The res_id could be scrambled up
        res_id = int(line[22:26])
        
        self._res_ids.append(res_id)
        self._is_amino.append(is_aminoacid)
        
        self.atom_res.append(resname)
        
        # Angstrom to nanometer
        self.atoms.append(Atom(atom_type, [x/10.0, y/10.0, z/10.0], name=name.strip()))
        
    def handle_CRYST(self, line):
        matched = re.match('(.{6})(.{9})(.{9})(.{9})(.{7})(.{7})(.{7})(.{11})(.{5})', line)
        tag, a, b, c, alpha, beta, gamma, group, zval = matched.groups()
        
        a = float(a)
        b = float(b)
        c = float(c)
        
        alpha = float(alpha)
        beta = float(beta)
        gamma = float(gamma)
        
        self._box_vectors = np.array([[a/10, 0, 0],
                                      [0, b/10, 0],
                                      [0, 0, c/10]])
    
    def handle_SHEET(self, line):
        tag = line[0:6]
        residue_start = int(line[22:26])
        residue_end = int(line[33:37])
        
        self._sheets.append((residue_start, residue_end))
    
    def handle_HELIX(self, line):
        # tag = line[22:18]
        residue_start = int(line[21:25])
        residue_end = int(line[33:37])
        
        self._helix.append((residue_start, residue_end))
        
    def get_system(self):
        r_array = np.array([a.r for a in self.atoms])
        type_array = np.array([a.type for a in self.atoms])
        atom_export = np.array([a.export for a in self.atoms])
        name = np.array([a.name for a in self.atoms])
        
        maps = { ('atom', 'residue') : [] }
        c = count()
        
        residue_names = []
        # Convert ids
        
        for (key, idx), group in groupby(zip(self.atom_res, self._res_ids)):
            molidx = next(c)
            maps['atom', 'residue'].extend([molidx]* len(list(group)))
            residue_names.append(key)

        s =  Molecule.from_arrays(r_array=r_array,
                                  type_array=type_array,
                                  maps=maps,
                                  atom_export=atom_export,
                                  residue_name=residue_names,
                                  atom_name=name)
                                # box_vectors=self._box_vectors
        
        res2mol = {k: i for i, k in enumerate(np.unique(self._res_ids))}
        i = 0
        
        # The default is coil
        n_residue = len(res2mol)
        
        for j, k in enumerate(np.unique(self._res_ids)):
            if self._is_amino[j]:
                s.secondary_structure[j] = 'C'
        
        # Secondary structure information
        for sheet in self._sheets:
            start = res2mol[sheet[0]]
            end = res2mol[sheet[1]] + 1
            s.secondary_structure[start:end] = 'E'
            s.secondary_id[start:end] = i + 1
            i += 1
        
        for helix in self._helix:
            start = res2mol[helix[0]]
            end = res2mol[helix[1]] + 1
            s.secondary_structure[start:end] = 'H'
            s.secondary_id[start:end] = i + 1
            i += 1

        # We take any contiguous coil and assign an ID to them
        ss_prev = ''
        j_prev = 0
        
        # print s.secondary_structure
        for j, ss in enumerate(s.secondary_structure):
            if ss_prev != ss:
                if ss_prev == 'C':
                    s.secondary_id[j_prev:j] = i + 1
                    i += 1
                
                ss_prev, j_prev = ss, j
        
        return System([s], box_vectors=self._box_vectors)
    
    def get_molecule(self):
        m = Molecule(self.atoms)
        return m
        
    def write(self, feature, sys):
        self.set_header()
        self.set_title()
        self.set_expdta()

        if feature == 'system':
            write_pdb(sys, self.fd,self.header,self.title,self.expdta)
        elif feature == 'molecule':
            write_pdb(sys, self.fd,self.header,self.title,self.expdta)

    def set_header(self,msg=None,date=None,code=None):
        # Called to set the header of the file. Callend upon init to 
        # give some default values.
        from datetime import datetime
        now = datetime.now()
        if date is None: # Default date
            date = now.strftime("%d-%b-%y")
        if msg is None: # Default header message
            msg = 'Generated with chemlab'
        if code is None: # Default code. The code doesn't really matter unless the file is submitted to the pdb itself. 
            code = '1111'
        while len(msg) < 40:
            msg = '{msg} '.format(msg=msg)
        head = 'HEADER    {msg}{date}    {code}\n'.format(msg=msg[:40],date=date,code=code)
        self.header = head
        
        return
    
    def set_title(self,title=None):
        # Called to set the title. init apply "No Title" by default. 
        if title is None: #default value
            title = 'No title'
        num = 1
        split_title = title.split()
        self.title = []
        line = 'TITLE     '
        while len(split_title) > 0: #split the title to multiple lines
            word = split_title[0]
            nextline = '{line} {word}'.format(line=line,word=word)
            if len(line) > 65:
                num += 1
                line = '{line}\n'.format(line=line)
                self.title.append(line)
                line = 'TITLE    {i} '.format(i=num)
                continue
            line = nextline
            split_title.remove(word)
        line = '{line}\n'.format(line=line)
        self.title.append(line)
        return

    def set_expdta(self,expdta=None):
        # Called to set the experimant data. The default is solution NMR. expdata is a list of either the indexes of the available options (see the list below) or something valid from the list. If invalid option is given, the value is set back to solution NMR
        valids = ['X-RAY  DIFFRACTION',
                  'FIBER  DIFFRACTION',
                  'NEUTRON  DIFFRACTION',
                  'ELECTRON  CRYSTALLOGRAPHY',
                  'ELECTRON  MICROSCOPY',
                  'SOLID-STATE  NMR',
                  'SOLUTION  NMR',
                  'SOLUTION  SCATTERING']
        if expdta is None: #default
            expdta = [valids[6]]

        for v in expdta:
            if isinstance( v, int):
                if v <0 or v >= len(valids): 
                    expdta = [valids[6]]
                    break
            if v not in valids:
                expdta = [valids[6]]
                break
        self.expdta = []
        line = 'EXPDTA     '
        num = 1
        while len(expdta) > 0: #split the title to multiple lines
            method = expdta[0]
            nextline = '{line} {method}'.format(line=line,method=method)
            if len(line) > 65:
                num += 1
                line = '{line}\n'.format(line=line)
                self.expdta.append(line)
                line = 'EXPDTA    {i} '.format(i=num)
                continue
            line = nextline
            expdta.remove(method)
        line = '{line}\n'.format(line=line)
        self.expdta.append(line)
        return


def write_pdb(sys,fd,header,title,expdta):
    from datetime import datetime
    # Writing the header
    fd.write(header)
    # Writing the title
    for line in (title):
        fd.write(line)
    #Writing the experimental data
    for line in (expdta):
        fd.write(line)
    #Writing the atoms
    index = 0
    connect = dict()
    for i in range (sys.n_mol):
        amol = sys.molecules[i]
        offset = sys.mol_indices[i]
        kwargs = amol.to_dict()
        bonds = kwargs['bonds'] or []
        
        for bond in bonds:
            #Creating a dictionary with all the bonds
            a = bond[0] + offset
            b = bond[1] + offset
            if not a in connect:
                connect[a] = []
            connect[a].append(b)
        for j in range (sys.mol_n_atoms[i]):
            #Atom name. 
            try:
                at_name = sys.atom_export[offset+j]['pdb.type']
            except KeyError:
                raise Exception('Atom type not provided')
            #Group name
            try:
                het_name = sys.atom_export[offset+j]['pdb.het_name']
            except KeyError:
                het_name = at_name
            # Charge
            try:
                charge = sys.charge_array
            except KeyError:
                charge = 0
            #Coordinates
            x,y,z = sys.r_array[offset+j]
            index += 1
            #From here, we generate the hetatm line
            line = 'HETATM'

            #The atom index
            stri = str(index)
            while len(line) + len(stri) < 11:
                line = '{line} '.format(line=line)
            line = '{line}{stri}'.format(line=line,stri=stri)

            #The atom name
            while len(line)+len(at_name) < 16:
                line = '{line} '.format(line=line)
            line = '{line}{at_name}'.format(line=line, at_name=at_name)
            
            #The molecule name
            while len(line)+len(het_name) < 20:
                line = '{line} '.format(line=line)
            line ='{line}{het_name}  '.format(line=line,het_name=het_name)

            # The molecule index. I'm not certain how it's used
            while len(line)+len(str(i)) < 26:
                line = '{line} '.format(line=line)
            line = '{line}{resSeq}    '.format(line=line,resSeq = str(i))
 
            #Position
            line = '{line}{x:>8.3f}{y:>8.3f}{z:8.3f}  '.format(line=line,x=x,y=y,z=z)
            # Occupancy and temp factror. I don't know how to use these
            line = '{line}1.00  0.00'.format(line=line)
            
            #Elemnt type
            while len(line) + len(at_name)< 78:
                line = '{line} '.format(line=line)
            line = '{line}{at_name}'.format(line=line, at_name = at_name)

            #Charge
            while len(line)+len(str(charge)) < 80:
                line = '{line} '.format(line=line)
            line = '{line}{charge}\n'.format(line=line,charge=str(charge))
            fd.write(line)
    #Writing the bonds
    connect_values = []
    for k in connect: connect_values.append(k)
    connect_values.sort()
    for atoma in connect_values:
        atomlist = connect[atoma]
        line = 'CONECT{:>4}'.format(atoma)
        count = 0
        for atomb in connect[atoma]:
            line = '{line}{atom:>4}'.format(line=line, atom=atomb)
            count += 1
            if count == 4:
                line = '{line}\n'.format(line=line)
                fd.write(line)
                line = 'CONECT{:>4}'.format(atoma)
        line = '{line}\n'.format(line=line)
        fd.write(line)


def checkWater(molIn):   
    # A function to check if a molecule is a water molecule. The use is streight forward
    # First the function check if there are 3 atoms in it, if not, return False
    # Second, we check that there are exactly 1 oxygene and two hydrogene atoms
    # Third we check that the bonds are correct. 
    kwargs = molIn.to_dict()
    atoms = kwargs['type_array']
    bonds = kwargs['bonds']

    posO = -1
    posH1 = -1
    posH2 = -1
    bondOH1 = False
    bondOH2 = False
    # Water molecules have exactly 3 atoms
    if not len (atoms) ==3: return False 
    # Checking the positions of each atom in the atoms list. We use this positions to be sure that there the right number of atoms
    for pos in range(len(atoms)):
        a = atoms[pos]
        if not a in ['O','H']: return False #Water molecules have only oxygene and hydrogene atoms
        if a == 'O': posO = pos 
        elif a == 'H' and posH1 == -1: posH1 = pos #First we store the position in posH1
        elif a == 'H': posH2 = pos #We only reach here when posH1 is a valid position. 
        elif a == 'O' and not posO == -1: return False #This mean there are two oxygene atoms here hance return False
    if posO == -1: return False #This mean there is no oxygene, hance, not a water molecule, return False
    #Now we check the bonds. 
    if len(bonds) == 0: #It is possible to define a moleucle without bonds. If this is so, we guess them.
        molIn.guess_bonds()
    bonds = molIn.to_dict()['bonds']
    for bond in bonds:
        if posO in bond and posH1 in bond: bondOH1 = True
        elif posO in bond and posH2 in bond: bondOH2 = True
    return bondOH1 and bondOH2



            
            
    
    

        
        

    
