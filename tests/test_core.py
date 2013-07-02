"""Test core types like Molecule and Atom.

"""
from chemlab.core import Molecule, Atom
from chemlab.core import System, subsystem_from_molecules, subsystem_from_atoms
from chemlab.core import merge_systems
from chemlab.core import crystal, random_lattice_box
import numpy as np
from nose.tools import eq_, assert_equals
from nose.plugins.attrib import attr
from chemlab.graphics import display_system


def assert_npequal(a, b):
    assert np.array_equal(a, b), '\n{} != {}'.format(a, b)


def assert_eqbonds(a, b):
    # compare bonds by sorting
    a = np.sort(np.sort(a, axis=0))
    b = np.sort(np.sort(b, axis=0))
    assert_npequal(a, b)


def assert_allclose(a, b):
    assert np.allclose(a, b), '\n{} != {}'.format(a, b)


def _make_water():
    mol = Molecule([Atom("O", [-4.99, 2.49, 0.0]),
                    Atom("H", [-4.02, 2.49, 0.0]),
                    Atom("H", [-5.32, 1.98, 1.0])],
                   bonds=[[0, 1], [0, 2]],
                   export={'hello': 1.0})
    return mol


class TestMolecule(object):
    def test_init(self):
        mol = _make_water()
        assert_npequal(mol.type_array, ['O', 'H', 'H'])


class TestSystem(object):
    def _make_molecules(self):
        wat = _make_water()
        wat.r_array *= 0.1
        # Initialization from empty
        s = System.empty(4, 4*3)

        mols = []
        # Array to be compared
        for _ in range(s.n_mol):
            wat.r_array += 0.1
            mols.append(wat.copy())
        return mols

    def _assert_init(self, system):
        assert_npequal(system.type_array, ['O', 'H', 'H',
                                           'O', 'H', 'H',
                                           'O', 'H', 'H',
                                           'O', 'H', 'H',])

        # Test atom coordinates
        #print "Atom Coordinates"
        #print s.r_array

        # Test atom masses
        #print s.m_array

        # Test charges
        assert_allclose(system.charge_array, [0.0, 0.0, 0.0,
                                              0.0, 0.0, 0.0,
                                              0.0, 0.0, 0.0,
                                              0.0, 0.0, 0.0])
        
        # Test mol indices
        assert_npequal(system.mol_indices, [0, 3, 6, 9])

        # Test mol n_atoms
        assert_npequal(system.mol_n_atoms, [3, 3, 3, 3])

        # Test get molecule entry
        assert_npequal(system.molecules[0].type_array, ['O', 'H', 'H'])

        # Test derived property -- center of mass
        assert_allclose(system.get_derived_molecule_array('center_of_mass'),
                        [[-1.00621917, 0.05572538, 0.02237967],
                         [-0.73978867, 0.07251013, 0.03916442],
                         [-0.47335818, 0.08929488, 0.05594917],
                         [-0.20692768, 0.10607963, 0.07273392]])

        # Test bonds
        assert_eqbonds(system.bonds, [[0, 1], [0, 2],
                                      [3, 4], [3, 5],
                                      [6, 7], [6, 8],
                                      [9, 10], [9, 11]])

        #print 'Test Indexing of system.molecule'
        #print s.molecules[0]
        #print s.molecules[:], s.molecules[:-5]
        #print s.atoms[0]
        #print s.atoms[:]

    def test_init(self):
        mols = self._make_molecules()
        system = System(mols)
        self._assert_init(system)

    def test_from_empty(self):
        mols = self._make_molecules()
        system = System.empty(4, 4*3)
        [system.add(mol) for mol in mols]
        self._assert_init(system)

    def test_from_arrays(self):
        mols = self._make_molecules()
        r_array = np.concatenate([m.r_array for m in mols])
        type_array = np.concatenate([m.type_array for m in mols])
        mol_indices = [0, 3, 6, 9]
        bonds = np.concatenate([m.bonds + 3*i for i, m in enumerate(mols)])

        system = System.from_arrays(r_array=r_array,
                                    type_array=type_array,
                                    mol_indices=mol_indices,
                                    bonds=bonds)

        self._assert_init(system)

    def test_subsystem_from_molecules(self):
        mols = self._make_molecules()
        system = System(mols)
        subsystem = subsystem_from_molecules(system, np.array([0, 2]))
        assert_equals(subsystem.n_mol, 2)

    def test_subsystem_from_atoms(self):
        mols = self._make_molecules()
        system = System(mols)
        sub = subsystem_from_atoms(system, np.array([True, True, False,
                                                     False, False, False,
                                                     False, False, False]))
        assert_equals(sub.n_mol, 1)

    def test_remove_atoms(self):
        # This will remove the first and last molecules
        mols = self._make_molecules()
        system = System(mols)
        system.remove_atoms([0, 1, 11])

        assert_eqbonds(system.bonds,
                       [[0, 1], [0, 2],
                        [3, 4], [3, 5]])
        assert_npequal(system.type_array,
                       np.array(['O', 'H', 'H', 'O', 'H', 'H'],
                                dtype='object'))

    def test_reorder_molecules(self):
        mols = self._make_molecules()
        system = System(mols)
        system.bonds = np.array([[0, 1], [3, 5]])
        # Reordering
        system.reorder_molecules([1, 0, 2, 3])
        assert_eqbonds(system.bonds, [[0, 2],
                                      [3, 4]])


@attr('slow')
def test_merge_system():
    # take a protein
    from chemlab.io import datafile
    from chemlab.graphics import display_system

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

    display_system(s, 'ball-and-stick')


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

    # Adding bonds
    s = System.empty(2, 2*bz.n_atoms)
    s.add(bz)
    assert_npequal(s.bonds, bz.bonds)
    s.add(bz)
    assert_npequal(s.bonds, np.concatenate((bz.bonds, bz.bonds + 6)))

    # Reordering
    orig = np.array([[0, 1], [6, 8]])
    s.bonds = orig
    s.reorder_molecules([1, 0])
    assert_npequal(s.bonds, np.array([[6, 7], [0, 2]]))

    # Selection
    ss = subsystem_from_molecules(s, [1])
    assert_npequal(ss.bonds, np.array([[0, 1]]))

    ss2 = System.from_arrays(**ss.__dict__)
    ss2.r_array += 10.0
    ms = merge_systems(ss, ss2)
    assert_npequal(ms.bonds, np.array([[0, 1], [6, 7]]))

    # From_arrays
    s = System.from_arrays(mol_indices=[0], **bz.__dict__)
    assert_npequal(s.bonds, bz.bonds)

    # Get molecule entry

    # Test the bonds when they're 0
    s.bonds = np.array([])
    assert_equals(s.get_derived_molecule_array('formula'), 'C6')

def test_random():
    '''Testing random made box'''
    from chemlab.db import ChemlabDB
    cdb = ChemlabDB()
    na = Molecule([Atom('Na', [0.0, 0.0, 0.0])])
    cl = Molecule([Atom('Cl', [0.0, 0.0, 0.0])])
    wat = cdb.get("molecule", 'gromacs.spce')

    s = random_lattice_box([na, cl, wat], [160, 160, 160], [4, 4, 4])

    #display_system(s)


def test_bond_guessing():
    from chemlab.db import ChemlabDB, CirDB
    from chemlab.graphics import display_molecule
    from chemlab.io import datafile

    mol = datafile('tests/data/3ZJE.pdb').read('molecule')
    print(mol.r_array)
    mol.guess_bonds()
    assert mol.bonds.size > 0

    # We should find the bond guessing also for systems

    # System Made of two benzenes
    bz = datafile("tests/data/benzene.mol").read('molecule')
    bzbonds = bz.bonds
    bz.bonds = np.array([])

    # Separating the benzenes by large amount
    bz2 = bz.copy()
    bz2.r_array += 2.0

    s = System([bz, bz2])
    s.guess_bonds()
    assert_eqbonds(s.bonds, np.concatenate((bzbonds, bzbonds + 6)))

    # Separating benzenes by small amount
    bz2 = bz.copy()
    bz2.r_array += 0.15

    s = System([bz, bz2])
    s.guess_bonds()
    assert_eqbonds(s.bonds, np.concatenate((bzbonds, bzbonds + 6)))

    #display_molecule(mol)



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
    print(na_atom.copy())

    print(s.v_array)

    # Try to adapt
    orig_s = s.astype(System)
    s = orig_s.astype(MySystem) # We lost the v information by converting back and forth

    print(orig_s, s)
    print(s.v_array)

    # Adapt for molecule and atoms
    print(type(na.astype(Molecule)))

    na_atom = MyAtom.from_fields(type='Na', r=[0.0, 0.0, 0.0], v=[1.0, 0.0, 0.0])
    print(type(na_atom.astype(Atom)))

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
