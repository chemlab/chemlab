# ITP file
import sys

unique = set()

opls_grotype = []

# This is to parse itp files
def parse(FILE):
    lines = open(FILE).readlines()
    
    # Let's tokenize all this stuff
    lines = [l for l in lines if l[0] != ';'] # Remove comments
    lines = [l for l in lines if l != '\n'] # Remove void line
    
    
    atomstatements = []
    
    state = 'start'
    for l in lines:
        # print state, l
        if state == 'start':
            if '[ atoms ]' in l:
                state = 'in atoms'
                atomslines = []
        elif state == 'in atoms':
            if '[' in l or l.startswith('#'):
                state = 'start'
                atomstatements.append(atomslines)
            else:
                atomslines.append(l)
                
    print FILE, len(atomstatements)
    #for st in atomstatements:
    #    print ''.join(st)
        
    # unique names
    for st in atomstatements:
        for l in st:
            fields = l.split()
            if len(fields) == 4:
                opls_grotype.append((fields[1], fields[0]))
            elif len(fields) == 7:
                opls_grotype.append((fields[1],fields[4]))
            elif len(fields) == 8:
                opls_grotype.append((fields[1], fields[4]))
            elif len(fields) == 6:
                opls_grotype.append((fields[1], fields[0]))
            else:
                print fields
                
from chemlab.db import masses
opls_to_type = {}
# Parse atp file
def parse_atp(file):
    lines  = open(file).readlines()
    # Let's tokenize all this stuff
    lines = [l for l in lines if l[0] != ';'] # Remove comments
    lines = [l for l in lines if l != '\n'] # Remove void line
    
    #print ''.join(lines)
    fields = [l.split()[:2] for l in lines]
    

    for opls, mass in fields:
        mass = float(mass)
        found = False
        for k, v in masses.typetomass.items():
            if abs(v - mass) < 0.1:
                type = k
                found = True
            
        if found:
            opls_to_type[opls] = type
        else:
            print 'Type', opls, 'not found.', 'Mass =', mass
            opls_to_type[opls] = 'Unknown'
    
parse_atp('/usr/share/gromacs/top/oplsaa.ff/atomtypes.atp')    
#parse_atp('/usr/share/gromacs/top/gmx.ff/atomtypes.atp')

for fn in sys.argv[1:]:
    parse(fn)

opls_grotype = set(opls_grotype)

grotype_to_type = {}
for opls, grotype in opls_grotype:
    grotype_to_type[grotype] = opls_to_type[opls]
    
from pprint import pprint
pprint(grotype_to_type)