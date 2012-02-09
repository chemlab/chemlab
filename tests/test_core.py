"""Test core types like Molecule and Atom.

"""
from chemlab import Molecule, Atom, readgeom
import numpy as np
import unittest

def test_init():
    """Test initialization of the Molecule and Atom classes."""
    # Default units for coordinates are Angstroms
    
    Molecule([Atom(1,"O", [0.0, 1.0, 0.0]),
             Atom(2,"H", [1.0, 0.0, 0.0]),
             Atom(3,"H", [0.0, 0.0, 1.0])],[])


class MoleculeTest(unittest.TestCase):
    """Test various functionalities of the molecule class."""

    def setUp(self):
        self.mol = Molecule([Atom(1,"O", [0.0, 1.0, 0.0]),
                             Atom(2,"H", [1.0, 0.0, 0.0]),
                             Atom(3,"H", [0.0, 0.0, 1.0])],[])

    def test_coords(self):
        """Tests the sanity of the coordinates for each atom."""
        assert all(self.mol.atoms[0].coords == np.array([0.0, 1.0, 0.0]))
        assert all(self.mol.atoms[1].coords == np.array([1.0, 0.0, 0.0]))
        assert all(self.mol.atoms[2].coords == np.array([0.0, 0.0, 1.0]))

    def test_symbol(self):
        """Tests the correctness of the atom symbol."""
        symbols = ["O", "H", "H"]
        for i, atom in enumerate(self.mol.atoms):
            assert atom.type == symbols[i]
            
    def test_bonds(self):
        """Tests if the bonds are created"""
        print self.mol.bonds
        assert (self.mol.bonds[0].id_bonded == [1,2])
        assert (self.mol.bonds[1].id_bonded == [1,3])
        
    def test_angles(self):
        """Test if the angles are created"""
        pass

  #   def test_coordarray(self):
#         """Test the sanity of the coordinates array."""
#         assert all(self.mol.coordsarray ==
#                    np.array([0.0, 1.0, 0.0,
#                              1.0, 0.0, 0.0,
#                              0.0, 0.0, 1.0]))
