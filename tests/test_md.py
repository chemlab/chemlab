'''Molecular Dynamics tests with uff'''
import numpy as np
from chemlab.core import *

stretch_k_ij = {
    ('H_','H_') : 1.0
}

bond_r_ij = {
    ('H_','H_') : 0.354 + 0.354,
}

def calculate_energy(r_array, mdtype_array, bonds):
    r_ij = bond_r_ij
    k_ij = stretch_k_ij
    
    en = 0
    # Bond stretching part
    for i_1, i_2 in bonds:
        t_1 = mdtype_array[i_1]
        t_2 = mdtype_array[i_2]
        r = np.linalg.norm(r_array[i_1] - r_array[i_2])
        en += 0.5 * k_ij[(t_1, t_2)] * (r - r_ij[(t_1, t_2)])
    
    return en

def test_uff():
    # Test a thing with one bond, like H2
    
    mol = Molecule([Atom('H', [0.0, 0.0, 0.0]), Atom('H', [0.3, 0.0, 0.0])])
    mol.bonds = np.array([[0, 1]])

    # Calculate the energy
    en = calculate_energy(mol.r_array, ['H_', 'H_'], bonds=mol.bonds)
    print(en)
    