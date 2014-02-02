import numpy as np
from chemlab.core import Atom, Molecule, System
from chemlab.graphics import display_system

# Spacing between two grid points
spacing = 0.3

# an 8x8x8 grid, for a total of 512 points
grid_size = (8, 8, 8)

# Preallocate the system
# 512 molecules, and 512*3 atoms
s = System.empty(512, 512*3)

# Water template, it contains export informations for gromacs
# more about export later...
water_tmp = Molecule([Atom('O', [0.0, 0.0, 0.0], export={'grotype': 'OW'}),
                      Atom('H', [0.1, 0.0, 0.0], export={'grotype': 'HW1'}),
                      Atom('H', [-0.03333, 0.09428, 0.0], export={'grotype':'HW2'})],
                     export={'groname': 'SOL'})

for a in range(grid_size[0]):
    for b in range(grid_size[1]):
        for c in range(grid_size[2]):
            grid_point = np.array([a,b,c]) * spacing # array operation
            water_tmp.move_to(grid_point)
            s.add(water_tmp)

# Adjust boxsize for periodic conditions
s.box_vectors = np.eye(3) * 8 * spacing

# Visualize to verify that the system was setup correctly
# display_system(s)

from chemlab.io import datafile

datafile("start.gro", "w").write("system", s)
