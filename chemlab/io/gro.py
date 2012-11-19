from ..core.system import System
from ..core.molecule import Atom

from ..data.symbols import symbol_list
import re

symbol_list = [s.lower() for s in symbol_list]


gro_to_cl = {
'OW' : 'O',
'HW1': 'H',
'HW2': 'H'}

def parse_gro(filename):
    with open(filename) as fn:
        lines = fn.readlines()
        title = lines.pop(0)
        natoms = int(lines.pop(0))
        atomlist = []
        for l in lines:
            fields = l.split()
            if len(fields) == 6:
                #Only positions are provided
                molidx = int(l[0:5])
                moltyp = l[5:10].strip()
                attyp = l[10:15].strip()
                atidx  = int(l[15:20])
                rx     = float(l[20:28])
                ry     = float(l[28:36])
                rz     = float(l[36:42])
                
                # Do I have to convert back the atom types, probably yes???
                if attyp.lower() not in symbol_list:
                    attyp = gro_to_cl[attyp]
                
                atomlist.append(Atom(attyp, [rx, ry, rz]))                

            if len(fields) == 3:
                # This is the box size
                boxsize = float(fields[0])
                return System(atomlist, boxsize)

