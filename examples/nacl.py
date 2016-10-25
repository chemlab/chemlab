from chemlab.core import Atom, Molecule, crystal
from chemlab.graphics.qt import display_system

# Molecule templates
na = Molecule([Atom('Na', [0.0, 0.0, 0.0])])
cl = Molecule([Atom('Cl', [0.0, 0.0, 0.0])])

s = crystal([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]], # Fractional Positions
            [na, cl], # Molecules
            225, # Space Group
            cellpar = [.54, .54, .54, 90, 90, 90], # unit cell parameters
            repetitions = [5, 5, 5]) # unit cell repetitions in each direction

display_system(s)
