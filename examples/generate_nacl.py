'''Generating a box of liquid water and NaCl'''
from chemlab import Atom, Molecule, System

# We should unify the Atom and Molecule objects
# into a thing called 'Body'

# Take the water molecule

# Molecule(Atom('H'), Atom('H'), Atom('O'))
# Molecule.from_string('water')

water = Molecule(Atom('O', [0.0, 0.0, 0.0]),
                 Atom('H', [0.1, 0.0, 0.0]),
                 Atom('H', [-0.03333, 0.09428, 0.0]))

# Put the water molecules randomly into the Box

# System.random_add(water, condition=)
sys = System(boxsize=10.0)

sys.random_add(water, min_distance=1.0)

# Exchange some water molecule with Na and Cl ions
# System.random_replace(cl, condition=)
# System.random_replace(na, condition=)

sys.random_replace(Atom('Cl', [0.0, 0.0, 0.0]))
# Generate the gro file
# save_system(sys, 'wbox.gro')