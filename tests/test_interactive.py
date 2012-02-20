"""These tests are meant to be ran with the utility *nosetests* and
they require interaction with the user.

"""
import chemlab as cl
from mock import Mock
import numpy as np

def test_read_and_display():
    """Read a molecule from disk and display it with the molecular
    viewer.

    """

    mol = cl.readgeom("tests/data/tink.xyz", format="tinkerxyz")
    cl.display(mol)

def test_display_molecule():
    """Display a molecule in the viewer using the viewer interface"""

    mol = Mock()

    at_params = [("C", (0.0, 0.0, 1.0)),
                 ("C", (0.0, 1.0, 0.0)),
                 ("H", (1.0, 0.0, 0.0)),
                 ("O", (1.0, 1.0, 1.0))]
    
    mol.atoms = []
    for sym, pos in at_params:
        at = Mock()
        at.coords = np.array(pos)
        at.type = sym
        
        mol.atoms.append(at)

    bond_params = [(0, 1), (1,2), (2,3)]
    mol.bonds = []
    for s,e in bond_params:
        bond = Mock()
        bond.start = mol.atoms[s]
        bond.end = mol.atoms[e]
        
        mol.bonds.append(bond)

    vw = cl.Viewer()
    vw.molecule = mol
    vw.show()