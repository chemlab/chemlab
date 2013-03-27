"""Test core types like Molecule and Atom.

"""
from chemlab import Molecule, Atom
from chemlab.core import System, subsystem_from_molecules, subsystem_from_atoms
from chemlab.core import crystal
import numpy as np
import unittest

def test_molecule():
    """Test initialization of the Molecule and Atom classes."""
    # Default units for coordinates are Angstroms
    
    mol = Molecule([Atom("O", [-4.99, 2.49, 0.0]),
                    Atom("H", [-4.02, 2.49, 0.0]),
                    Atom("H", [-5.32, 1.98, 1.0])],[])

def _print_sysinfo(s):
    print "Atom Coordinates"
    print s.r_array
    
    print "Atom Masses"
    print s.m_array
    
    print "Atom Arrays"
    print s.type_array
    
    print "Molecule Starting Indices"
    print s.mol_indices
    
    print "Molecules' number of atoms"
    print s.mol_n_atoms

    print 'This an array with all center of masses'
    print s.get_derived_molecule_array('center_of_mass')
    
    print 'Test Indexing of system.molecule'
    print s.molecules[0]
    print s.molecules[:], s.molecules[:-5]

    print s.atoms[0]
    print s.atoms[:]
    
def test_system():
    wat = Molecule([Atom("O", [-4.99, 2.49, 0.0]),
                    Atom("H", [-4.02, 2.49, 0.0]),
                    Atom("H", [-5.32, 1.98, 1.0])])

    wat.r_array *= 0.1
    # Initialization from empty
    s = System.empty(4, 4*3)
    
    mols = []
    for i in xrange(s.n_mol):
        wat.r_array += 0.1
        s.add(wat)
        m  = wat.copy()
        mols.append(wat.copy())
        
    # Printing just to test if there aren't any exception    
    print "Init from Empty"
    print "*" * 72
    _print_sysinfo(s)
    
    print "Init Normal"
    print "*" * 72
    s = System(mols)
    _print_sysinfo(s)
    
    # 3 water molecules
    r_array = np.random.random((9, 3))
    type_array = ['O', 'H', 'H', 'O', 'H', 'H', 'O', 'H', 'H']
    mol_indices = [0, 3, 6]
    mol_n_atoms = [3, 3, 3]
    s2 = System.from_arrays(r_array=r_array, type_array=type_array,
                       mol_indices=mol_indices, mol_n_atoms=mol_n_atoms)
    
    
    sub2 = subsystem_from_molecules(s2, np.array([0, 2]))
    assert sub2.n_mol == 2
    
    
    sub = subsystem_from_atoms(s2, np.array([True, True, False,
                                             False, False, False,
                                             False, False, False]))
    assert sub.n_mol == 1
    

def test_crystal():
    '''Building a crystal by using spacegroup module'''
    na = Molecule([Atom('Na', [0.0, 0.0, 0.0])])
    cl = Molecule([Atom('Cl', [0.0, 0.0, 0.0])])
    
    # Fract position of Na and Cl, space group 255
    tsys = crystal([[0.0, 0.0, 0.0],[0.5, 0.5, 0.5]], [na, cl], 225, repetitions=[13,13,13])
