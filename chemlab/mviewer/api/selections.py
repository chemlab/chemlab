import numpy as np

from chemlab.mviewer.representations.state import Selection
from chemlab.core import subsystem_from_atoms

from core import *

def select_atom_type(name):
    '''Select atoms by their type.

    You can select all the hydrogen atoms as follows::
    
      select_atom_type('H')
    
    '''
    mask = current_system().type_array == name
    return select_atoms(mask.nonzero()[0])


def select_atoms(indices):
    '''Select atoms by their indices.

    You can select the first 3 atoms as follows::

      select_atoms([0, 1, 2])
    
    Return the current selection dictionary.

    '''
    rep = current_representation()
    rep.select({'atoms': Selection(indices, current_system().n_atoms)})
    return rep.selection_state


def select_selection(selection):
    '''Select a selection object'''
    rep = current_representation()
    rep.select(selection)
    return rep.selection_state
    

def select_all():
    '''Select all the visible atoms.
    
    '''
    
    return select_atoms(visible_atoms())


def clear_selection():
    '''Clear the current selection.'''
    return select_atoms([])
    

def invert_selection():
    '''Invert the current selection. Select the currently unselected
    atoms.

    '''
    indices = current_representation().selection_state['atoms'].invert().indices
    return select_atoms(indices)

def select_molecules(name):
    '''Select all the molecules corresponding to the formulas.'''
    mol_formula = current_system().get_derived_molecule_array('formula')
    mask = mol_formula == name
    ind = current_system().mol_to_atom_indices(mask.nonzero()[0])
    return select_atoms(ind)
    
def visible_atoms():
    '''Return the indices of the currently visible atoms.'''
    return current_representation().hidden_state['atoms'].invert().indices



def hide_selected():    
    '''Hide the selected objects.'''
    current_representation().hide(current_representation().selection_state)


def hide_water():
    '''Conveniency command to hide water molecules.'''
    select_molecules('H2O')
    hide_selected()


def unhide_all():
    '''Unhide all the objects'''
    return current_representation().hide(
        {'atoms': Selection([],current_system().n_atoms),
         'bonds': Selection([], current_system().n_bonds)})

# def delete():
#     s = current_system()
#     s = subsystem_from_atoms(s, ~current_selection().atom_selection_mask)
    
#     # Fix also trajectory
#     coords = current_trajectory()
#     for i, c in enumerate(coords):
#         coords[i] = c[~current_selection().atom_selection_mask]
    
#     display(s)
    

def selected_atoms():
    '''The indices of the currently selected atoms.'''
    rep = current_representation()
    
    return rep.selection_state['atoms'].indices


def visible_to_original(visible_index):
    return (~current_representation().hidden_state.atom_hidden_mask).nonzero(0)
