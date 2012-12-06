'''Generating a box of liquid water and NaCl'''
from chemlab import Atom, Molecule, System
from chemlab.graphics import display_system

# We should unify the Atom and Molecule objects
# into a thing called 'Body'

# Take the water molecule

# Molecule(Atom('H'), Atom('H'), Atom('O'))
# Molecule.from_string('water')

water = Molecule([Atom('O', [0.0, 0.0, 0.0]),
                 Atom('H', [0.1, 0.0, 0.0]),
                 Atom('H', [-0.03333, 0.09428, 0.0])])

# Put the water molecules randomly into the Box
sodium = Molecule([Atom('Cl', [0.0, 0.0, 0.0])])
chloride = Molecule([Atom('Na', [0.0, 0.0, 0.0])])

# System.random_add(water, condition=)
sys = System(boxsize=2.0)

wat_density = 33.435

nmol = int(wat_density * sys.boxsize**3)

for i in range(nmol):
    if 0 < i < 15:
        sys.random_add(sodium.copy(), 0.4, 1000)
    if 15 < i < 30:
        sys.random_add(chloride.copy(), 0.4, 1000)
    else:
        sys.random_add(water.copy(), min_distance=0.25, maxtries = 1000)    
    
display_system(sys)

# Exchange some water molecule with Na and Cl ions
# System.random_replace(cl, condition=)
# System.random_replace(na, condition=)

# sys.random_replace(Atom('Cl', [0.0, 0.0, 0.0]))
# Generate the gro file
# save_system(sys, 'wbox.gro')