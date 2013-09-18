from core import *

def select_indices(indices):
    current_selection().select_atoms(indices)

def clear_selection():
    select_indices([])
    
def select_atoms(name):
    mask = current_system().type_array == name
    current_selection().select_atoms(mask)
    
def select_molecules(name):
    mol_formula = current_system().get_derived_molecule_array('formula')
    mask = mol_formula == name
    ind = current_system().mol_to_atom_indices(mask.nonzero()[0])
    current_selection().select_atoms(ind)
    
def visible_atoms():
    return (~viewer.representation.hidden_state.atom_hidden_mask).nonzero()[0]

    
def invert_selection():
    current_selection().select_atoms((~viewer.representation.selection_state.atom_selection_mask).nonzero()[0])
    
def unhide(sel=None):
    if sel == None:
        viewer.representation.hidden_state.hide_atoms([])
    
from chemlab.core import subsystem_from_atoms

def delete():
    s = current_system()
    s = subsystem_from_atoms(s, ~current_selection().atom_selection_mask)
    
    # Fix also trajectory
    coords = current_trajectory()
    for i, c in enumerate(coords):
        coords[i] = c[~current_selection().atom_selection_mask]
    
    display(s)
    
def selected_atoms():
    return current_selection().atom_selection

_selection_stack = []
def store_selection():
    _selection_stack.append(selected_atoms())

def add_selection():
    current_selection().select_atoms(_selection_stack[-1], mode='additive')
    
def flip_selection():
    current_selection().select_atoms(_selection_stack[-1], mode='flip')