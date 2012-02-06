"""Test core types like Molecule and Atom.

"""
from chemlab import Molecule, Atom, readgeom
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
        assert all(self.mol.atoms[0] == np.array([0.0, 1.0, 0.0]))
        assert all(self.mol.atoms[1] == np.array([1.0, 0.0, 0.0]))
        assert all(self.mol.atoms[2] == np.array([0.0, 0.0, 1.0]))

    def test_symbol(self):
        """Tests the correctness of the atom symbol."""
        symbols = ["O", "H", "H"]
        for i, atom in enumerate(self.mol.atoms):
            assert atom.symbol == symbols[i]

    def test_coordarray(self):
        """Test the sanity of the coordinates array."""
        assert all(self.mol.coordsarray ==
                   np.array([0.0, 1.0, 0.0,
                             1.0, 0.0, 0.0,
                             0.0, 0.0, 1.0]))

def bond_guessing_test():
    """Test if bonds are guessed properly."""
    mol = readgeom("tests/data/sulphoxide.xyz",format="xyz")
    
    assert isinstance(mol, Molecule)
    mol.guess_bonds()
    
    so_bond =  mol.get_bond(0, 1) # Not sure if getting a bond by
                                    # index tuple is a good idea

    assert so_bond, "The bond S-O doesn't exists"
    
    # Check if the bond order is 2, again, not sure if an order
    # attribute makes sense since we'll probably not support bond
    # orders like 2.5
    assert so_bond.order == 2

    sc_bond = mol.get_bond(1, 2)
    assert sc_bond
    assert sc_bond.order == 1
    
    ch_bond = mol.get_bond(2, 3)
    assert ch_bond
    assert ch_bond.order == 1

    # Verify if they at least correspond
    cc_benz_bond2 = mol.get_bond(8, 9)
    assert cc_benz_bond2
    assert cc_benz_bond2.order == 2
    
    cc_benz_bond1 = mol.get_bond(7, 8)
    assert cc_benz_bond1
    assert cc_benz_bond1.order == 1

    
    
    