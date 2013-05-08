"""Test core types like Molecule and Atom.

"""
from chemlab import Molecule, Atom
from chemlab.core import System, subsystem_from_molecules, subsystem_from_atoms
from chemlab.core import crystal, random_lattice_box
import numpy as np
import unittest
from chemlab.graphics import display_system
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
                    Atom("H", [-5.32, 1.98, 1.0])], export={'hello': 1.0})

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
    

    print 'bonds', s2._mol_bonds
    sub2 = subsystem_from_molecules(s2, np.array([0, 2]))
    assert sub2.n_mol == 2
    
    
    sub = subsystem_from_atoms(s2, np.array([True, True, False,
                                             False, False, False,
                                             False, False, False]))
    assert sub.n_mol == 1

def test_system_remove():
        # 3 water molecules
    r_array = np.random.random((9, 3))
    type_array = ['O', 'H', 'H', 'O', 'H', 'H', 'O', 'H', 'H']
    mol_indices = [0, 3, 6]
    mol_n_atoms = [3, 3, 3]
    s2 = System.from_arrays(r_array=r_array, type_array=type_array,
                       mol_indices=mol_indices, mol_n_atoms=mol_n_atoms)

    s2.remove_atoms([0, 1])
    
    print s2.type_array
    
def test_merge_system():
    # take a protein
    from chemlab.io import datafile
    from chemlab.graphics import display_system
    from chemlab.core import merge_systems
    from chemlab.db import ChemlabDB
    
    water = ChemlabDB().get("molecule", "example.water")
    
    prot = datafile("tests/data/3ZJE.pdb").read("system")
    
    # Take a box of water
    NWAT = 50000
    bsize = 20.0
    pos = np.random.random((NWAT, 3)) * bsize
    wat = water.copy()
    
    s = System.empty(NWAT, NWAT*3, box_vectors=np.eye(3)*bsize)
    for i in range(NWAT):
        wat.move_to(pos[i])
        s.add(wat)
    
    prot.r_array += 10
    s = merge_systems(s, prot, 0.5)

    display_system(s)
    
    
def test_crystal():
    '''Building a crystal by using spacegroup module'''
    na = Molecule([Atom('Na', [0.0, 0.0, 0.0])])
    cl = Molecule([Atom('Cl', [0.0, 0.0, 0.0])])
    
    # Fract position of Na and Cl, space group 255
    tsys = crystal([[0.0, 0.0, 0.0],[0.5, 0.5, 0.5]], [na, cl], 225, repetitions=[13,13,13])


def test_sort():
    na = Molecule([Atom('Na', [0.0, 0.0, 0.0])])
    cl = Molecule([Atom('Cl', [0.0, 0.0, 0.0])])
    
    # Fract position of Na and Cl, space group 255
    tsys = crystal([[0.0, 0.0, 0.0],[0.5, 0.5, 0.5]], [na, cl], 225, repetitions=[3,3,3])    
    
    tsys.sort()
    assert np.all(tsys.type_array[:tsys.n_mol/2] == 'Cl')

def test_bonds():
    from chemlab.io import datafile
    bz = datafile("tests/data/benzene.mol").read('molecule')
    na = Molecule([Atom('Na', [0.0, 0.0, 0.0])])
    
    s2 = System.empty(2, 2)
    s2.add(na)
    s2.add(na)
    s2.get_bond_array()
    
    s = System.empty(2, 2*bz.n_atoms)
    s.add(bz)
    s.add(bz)
    
    print s.get_bond_array()

def test_random():
    '''Testing random made box'''
    from chemlab.db import ChemlabDB
    cdb = ChemlabDB()
    na = Molecule([Atom('Na', [0.0, 0.0, 0.0])])
    cl = Molecule([Atom('Cl', [0.0, 0.0, 0.0])])
    wat = cdb.get("molecule", 'gromacs.spce')
    
    s = random_lattice_box([na, cl, wat], [160, 160, 160], [4, 4, 4])
    display_system(s)
    #random_box([na, cl, wat], [16, 16, 130], [10, 10, 10], rmin=0.2)


def test_bond_guessing():
    from chemlab.core.system import guess_bonds
    r_array = np.random.random((9, 3))
    type_array = ['O', 'H', 'H', 'O', 'H', 'H', 'O', 'H', 'H']
    mol_indices = [0, 3, 6]
    mol_n_atoms = [3, 3, 3]
    s2 = System.from_arrays(r_array=r_array, type_array=type_array,
                       mol_indices=mol_indices, mol_n_atoms=mol_n_atoms)
    print guess_bonds(s2)
    
def test_extending():
    from chemlab.core.attributes import NDArrayAttr, MArrayAttr
    from chemlab.core.fields import AtomicField
    
    class MySystem(System):
        attributes = System.attributes + [NDArrayAttr('v_array', 'v_array', np.float, 3)]
    
    class MyMolecule(Molecule):
        attributes = Molecule.attributes + [MArrayAttr('v_array', 'v', np.float)]
        
    class MyAtom(Atom):
        fields = Atom.fields + [AtomicField('v', default=lambda at: np.zeros(3, np.float))]
    
    na = MyMolecule([MyAtom.from_fields(type='Na', r=[0.0, 0.0, 0.0], v=[1.0, 0.0, 0.0])])
    cl = MyMolecule([MyAtom.from_fields(type='Cl', r=[0.0, 0.0, 0.0])])
    s = MySystem([na, cl])

    na_atom = MyAtom.from_fields(type='Na', r=[0.0, 0.0, 0.0], v=[1.0, 0.0, 0.0])
    print na_atom.copy()
    
    print s.v_array
    
    # Try to adapt
    orig_s = s.astype(System)
    s = orig_s.astype(MySystem) # We lost the v information by converting back and forth
    
    print orig_s, s
    print s.v_array

    # Adapt for molecule and atoms
    print type(na.astype(Molecule))
    
    na_atom = MyAtom.from_fields(type='Na', r=[0.0, 0.0, 0.0], v=[1.0, 0.0, 0.0])
    print type(na_atom.astype(Atom))

def test_serialization():
    cl = Molecule([Atom.from_fields(type='Cl', r=[0.0, 0.0, 0.0])])
    jsonstr =  cl.tojson()
    assert Molecule.from_json(jsonstr).tojson() == jsonstr

    na = Molecule([Atom('Na', [0.0, 0.0, 0.0])])
    cl = Molecule([Atom('Cl', [0.0, 0.0, 0.0])])
    
    # Fract position of Na and Cl, space group 255
    tsys = crystal([[0.0, 0.0, 0.0],[0.5, 0.5, 0.5]], [na, cl], 225, repetitions=[3,3,3])
    jsonstr = tsys.tojson()
    
    assert System.from_json(jsonstr).tojson() == jsonstr
    