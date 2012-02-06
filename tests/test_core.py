"""Test core types like Molecule and Atom.

"""
from chemlab import Molecule, Atom
import numpy as np


def test_init():
    """Test initialization of the Molecule and Atom classes."""
    # Default units for coordinates are Angstroms
    
    Molecule(Atom("O", [0.0, 1.0, 0.0]),
             Atom("H", [1.0, 0.0, 0.0]),
             Atom("H", [0.0, 0.0, 1.0]))


class MoleculeTest(object):
    """Test various functionalities of the molecule class."""

    def setUp(self):
        self.mol = Molecule(Atom("O", [0.0, 1.0, 0.0]),
                            Atom("H", [1.0, 0.0, 0.0]),
                            Atom("H", [0.0, 0.0, 1.0]))

    def test_coords(self):
        """Tests the sanity of the coordinates for each atom."""
        assert self.mol.atoms[0] == np.array([0.0, 1.0, 0.0])
        assert self.mol.atoms[1] == np.array([1.0, 0.0, 0.0])
        assert self.mol.atoms[2] == np.array([0.0, 0.0, 1.0])

    def test_symbol(self):
        """Tests the correctness of the atom symbol."""
        symbols = ["O", "H", "H"]
        for i, atom in enumerate(self.mol.atoms):
            assert atom.symbol == symbols[i]

    def test_coordarray(self):
        """Test the sanity of the coordinates array."""
        assert self.mol.coordsarray == np.array([0.0, 1.0, 0.0,
                                            1.0, 0.0, 0.0,
                                            0.0, 0.0, 1.0])