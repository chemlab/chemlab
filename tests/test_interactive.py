"""These tests are meant to be ran with the utility *nosetests* and
they require interaction with the user.

"""
import chemlab as cl
from mock import Mock
import numpy as np

from chemlab.graphics.renderers import AtomRenderer

class TodoException(Exception):
    pass

def test_read_and_display():
    """Read a molecule from disk and display it with the molecular
    viewer.

    """
    raise TodoException()

def test_display_molecule():
    """Display a molecule in the viewer using the viewer interface"""

    mol = Mock()

    at_params = [("C", (0.0, 0.0, 1.0)),
                 ("C", (0.0, 1.0, 0.0)),
                 ("H", (1.0, 0.0, 0.0)),
                 ("O", (1.0, 1.0, 1.0))]
    
    bond_params = [(0, 1), (1,2), (2,3)]
    raise TodoException()

from chemlab.graphics import colors
from chemlab.data.vdw import vdw_dict

def test_single_mol():
    v = cl.graphics.Viewer()
    mol = cl.readgeom("tests/data/tink.xyz", format="tinkerxyz")
    
    mol.r_array -= mol.geometric_center
    mol.r_array *= 0.1
    
    ar = v.add_renderer(AtomRenderer, mol.atoms)
    ar.colorlist[4] = [0, 255, 255, 255]    
    ar.update_positions(mol.r_array)
    ar.update_colors(ar.colorlist)
    
    v.run()
