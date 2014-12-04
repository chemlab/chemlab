
from ..db import CirDB
from chemview import MolecularViewer, enable_notebook

_state = {'chemview_initialized' : False}
if not _state['chemview_initialized']:
    enable_notebook()
    _state['chemview_initialized'] = True

def download_molecule(name):
    "Fetch a molecule from the web by its common name"

    return CirDB().get('molecule', name)


def display_molecule(molecule):
    topology = {
        'atom_types': molecule.type_array,
        'bonds': molecule.bonds
    }

    mv = MolecularViewer(molecule.r_array, topology)
    
    if molecule.n_bonds != 0:
        mv.points(size=0.15)
        mv.lines()
    else:
        mv.points()

    return mv

def display_system(system):
    return display_molecule(system)

def display_trajectory(system, frames):
    pass
