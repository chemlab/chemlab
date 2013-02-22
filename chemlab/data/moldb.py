from ..core import Molecule, Atom


na = Molecule([Atom('Na', [0.0, 0.0, 0.0], export={'grotype': 'NA'})], export={'groname': 'NA+'})
br = Molecule([Atom('Br', [0.0, 0.0, 0.0], export={'grotype': 'BR'})], export={'groname': 'BR-'})

li = Molecule([Atom('Li', [0.0, 0.0, 0.0], export={'grotype': 'LI'})], export={'groname': 'LI+'})
cl = Molecule([Atom('Cl', [0.0, 0.0, 0.0], export={'grotype': 'CL'})], export={'groname': 'CL-'})

water = Molecule([Atom('O', [0.0, 0.0, 0.0], export={'grotype': 'OW'}),
                  Atom('H', [0.1, 0.0, 0.0], export={'grotype': 'HW1'}),
                  Atom('H', [-0.03333, 0.09428, 0.0], export={'grotype':'HW2'})], export={'groname': 'SOL'})

