"""These tests are meant to be ran with the utility *nosetests* and
they require interaction with the user.

"""
import chemlab as cl

def test_read_and_display():
    """Read a molecule from disk and display it with the molecular
    viewer.

    """

    mol = cl.read_molecule("testmol.xyz", format="tinker")
    cl.display(mol)