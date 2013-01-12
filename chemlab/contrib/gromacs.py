'''A set of utilities to interact with gromacs'''

# Need to add a parser to insert this contrib script

# $ chemlab gromacs energy
# it should show a little interface to view the energy

# Let's launch the program and determine what happens

import pexpect

child = pexpect.spawn('g_energy')
child.expect('Select the terms you want')
for i in range(4):
    child.readline()

datatab = ''
while True:
    line = child.readline()
    datatab += line.lower()
        
    if line == '\r\n':
        #print 'done!'
        break
    
data_avail = datatab.split()[1::2]

import difflib
import sys

input_ = ''
for arg in sys.argv[1:]:
    match = difflib.get_close_matches(arg, data_avail)
    print 'Close Matches', match
    
    if match == []:
        print arg, ': No such property'
        sys.exit(0)

    prop = match[0]
    ind = data_avail.index(prop) + 1
    input_ += '%d '%ind

child.sendline(input_+'\n')
child.expect(pexpect.EOF)

# Now let's read the xvg file
import re

quantities = []
for line in open('energy.xvg'):
    if line[0] not in ['#', '@']:
        break
    
    if 'yaxis' in line:
        m = re.search("\"(.*)\"", line)
        units = m.group(1).split(', ')
    elif re.match('@ s\d+\s+legend', line):
        m = re.search("\"(.*)\"", line)
        quantities.append(m.group(1))

import numpy as np
from matplotlib import pyplot

# Finally display this with matplotlib
datamat = np.loadtxt('energy.xvg', comments='@', skiprows=8, unpack=True)
pyplot.plot(datamat[0], datamat[1])
pyplot.show()