'''Querying'''
from chemlab.core import System
from nose.tools import eq_
import numpy as np

def array_eq_(a, b):
    assert np.all(a == b)

def test_query():
    type_array = ['Cl', 'Cl', 'O', 'H', 'H', 'O', 'H', 'H', 'Na', 'Na']
    mol_indices = [0, 1, 2, 5, 8, 9]
    s = System.from_arrays(type_array = type_array, mol_indices=mol_indices)
    array_eq_(s.where(type_in=['Na', 'Cl']), 
              [True, True, False, False, False, False, False, False, True, True])
    
    array_eq_(s.where(type='Cl'), 
              [True, True, False, False, False, False, False, False, False, False])
    
    # We move the Cl away
    cl = s.where(type='Cl')
    s.r_array[cl.nonzero()[0]] = [1, 0, 0]
    s.box_vectors = np.diag([3, 3, 3])
    
    array_eq_(s.where(type_in=['H', 'O'], within_of=(0.2, [8, 9])),
             [False, False, True, True, True, True, True, True, False, False])
