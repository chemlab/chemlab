import numpy as np

from chemlab.mviewer.representations.state import Selection
from chemlab.core import subsystem_from_atoms

from .core import *

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
    '''Select a :class:`~chemlab.mviewer.Selection` object'''
    rep = current_representation()
    rep.select(selection)
    return rep.selection_state
    

def cancel_selection():
    '''Reset the current selection'''
    sel = current_selection()
    
    #for k, v in sel.items():
    #    sel[k].mask[:] = True

def select_all():
    '''Select all the visible atoms.'''
    
    return select_atoms(visible_atoms())

def select_connected_bonds():
    '''Select the bonds connected to the currently selected atoms.'''
    s = current_system()
    start, end = s.bonds.transpose()
    selected = np.zeros(s.n_bonds, 'bool')
    for i in selected_atoms():
        selected |= (i == start) | (i == end)

    csel = current_selection()
    bsel = csel['bonds'].add(
        Selection(selected.nonzero()[0], s.n_bonds))
    
    ret = csel.copy()
    ret['bonds'] = bsel

    return select_selection(ret)


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

    selection = {'atoms': Selection(ind, current_system().n_atoms)}

    # Need to find the bonds between the atoms
    b = current_system().bonds
    if len(b) == 0:
        selection['bonds'] = Selection([], 0)
    else:
        molbonds = np.zeros(len(b), 'bool')
        for i in ind:
            matching = (i == b).sum(axis=1).astype('bool')
            molbonds[matching] = True
        
        selection['bonds'] = Selection(molbonds.nonzero()[0], len(b))

    return select_selection(selection)
    
def visible_atoms():
    '''Return the indices of the currently visible atoms.'''
    return current_representation().hidden_state['atoms'].invert().indices



def hide_selected():    
    '''Hide the selected objects.'''
    ss = current_representation().selection_state
    hs = current_representation().hidden_state
    res = {}
    
    for k in ss:
        res[k] = hs[k].add(ss[k])
    
    current_representation().hide(res)


def hide_water():
    '''Conveniency command to hide water molecules.'''
    select_molecules('H2O')
    hide_selected()


def unhide_all():
    '''Unhide all the objects'''
    return current_representation().hide(
        {'atoms': Selection([],current_system().n_atoms),
         'bonds': Selection([], current_system().n_bonds)})
    
def unhide_selected():
    '''Unhide the selected objects'''
    
    hidden_state = current_representation().hidden_state
    selection_state = current_representation().selection_state

    res = {}
    # Take the hidden state and flip the selected atoms bits.
    for k in selection_state:
        visible = hidden_state[k].invert()
        visible_and_selected = visible.add(selection_state[k]) # Add some atoms to be visible
        res[k] = visible_and_selected.invert()
    
    current_representation().hide(res)


def current_selection():
    rep = current_representation()
    return rep.selection_state

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
    '''Transform the indexes of the visible atoms to the indexes of
    the total atoms.

    '''
    return (~current_representation().hidden_state.atom_hidden_mask).nonzero(0)
