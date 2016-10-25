"""Test core types like Molecule and Atom."""
from __future__ import division, print_function

import numpy as np
from nose.plugins.attrib import attr
from nose.tools import assert_equals, eq_, ok_

from chemlab.core import (System, crystal, merge_systems, random_box,
                          subsystem_from_atoms, subsystem_from_molecules,
                          random_lattice_box, Atom, Molecule)

from chemlab.table import vdw_radius
from chemlab.io import datafile

#from chemlab.graphics.qt import display_system
from .testtools import assert_allclose, assert_eqbonds, assert_npequal, npeq_


def _make_water():
    mol = Molecule([Atom("O", [-4.99, 2.49, 0.0]),
                    Atom("H", [-4.02, 2.49, 0.0]),
                    Atom("H", [-5.32, 1.98, 1.0])],
                   bonds=[[0, 1], [0, 2]],
                   export={'hello': 1.0})
    return mol


class TestAtom(object):
    def test_init(self):
        a = Atom("O", [-4.99, 2.49, 0.0])
        eq_(a.type_array, 'O')
        assert_npequal(a.r_array, [-4.99, 2.49, 0.0])


class TestMolecule(object):
    def test_init(self):
        mol = _make_water()
        eq_(mol.export, {'hello': 1.0})
        assert_npequal(mol.get_attribute('type_array').value, ['O', 'H', 'H'])
        assert_npequal(mol.type_array, ['O', 'H', 'H'])
        assert_npequal(mol.bonds, [[0, 1], [0, 2]])

        mol = Molecule.empty()
        eq_(mol.dimensions['atom'], 0)
        eq_(mol.dimensions['bond'], 0)

    def test_copy(self):
        mol = _make_water()
        mol2 = mol.copy()
        assert_npequal(mol2.type_array, mol.type_array)


class TestSystem(object):
    def _make_molecules(self):
        wat = _make_water()
        wat.r_array *= 0.1

        mols = []
        # Array to be compared
        for _ in range(4):
            wat.r_array += 0.1
            mols.append(wat.copy())
        return mols

    def _assert_init(self, system):
        assert_npequal(system.type_array, ['O',
                                           'H',
                                           'H',
                                           'O',
                                           'H',
                                           'H',
                                           'O',
                                           'H',
                                           'H',
                                           'O',
                                           'H',
                                           'H', ])

        # Test charges
        assert_allclose(system.charge_array, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                              0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        # Test mol indices
        assert_npequal(system.mol_indices, [0, 3, 6, 9])

        # Test mol n_atoms
        assert_npequal(system.mol_n_atoms, [3, 3, 3, 3])

        # Test get molecule entry
        assert_npequal(system.molecules[0].type_array, ['O', 'H', 'H'])

        # Test bonds
        assert_eqbonds(system.bonds, [[0, 1], [0, 2], [3, 4], [3, 5], [6, 7],
                                      [6, 8], [9, 10], [9, 11]])

    def test_init(self):
        mols = self._make_molecules()
        system = System(mols)
        self._assert_init(system)

    def test_from_batch(self):
        mols = self._make_molecules()

        system = System()
        with system.batch() as batch:
            [batch.append(mol) for mol in mols]
        self._assert_init(system)

    def test_from_empty(self):
        s = System.empty(molecule=3, atom=9, bonds=6)
        assert_npequal(s.type_array, [''] * 9)
        assert_npequal(s.molecule_name, [''] * 3)

    def test_from_actual_empty(self):
        mols = self._make_molecules()
        system = System([])
        [system.add(mol) for mol in mols]
        self._assert_init(system)

    def test_from_arrays(self):
        mols = self._make_molecules()
        system = System.from_arrays(
            r_array=np.concatenate([m.r_array for m in mols]),
            type_array=np.concatenate([m.type_array for m in mols]),
            bonds=np.concatenate([m.bonds + 3 * i for i, m in enumerate(mols)
                                  ]),
            maps={
                ('atom', 'molecule'): [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3],
                ('bond', 'molecule'): [0, 0, 1, 1, 2, 2, 3, 3]
            })
        self._assert_init(system)

    def test_subsystem_from_molecules(self):
        mols = self._make_molecules()
        system = System(mols)

        subsystem = subsystem_from_molecules(system, np.array([0, 2]))
        assert_equals(subsystem.n_mol, 2)

    def test_subsystem_from_atoms(self):
        mols = self._make_molecules()
        system = System(mols)
        sub = subsystem_from_atoms(system, np.array(
            [True, True, False, False, False, False, False, False, False]))
        assert_equals(sub.n_mol, 1)

    def test_remove_atoms(self):
        # This will remove the first and last molecules
        mols = self._make_molecules()
        system = System(mols)
        system.remove_atoms([0, 1, 11])

        assert_eqbonds(system.bonds, [[0, 1], [0, 2], [3, 4], [3, 5]])
        assert_npequal(system.type_array,
                       np.array(['O', 'H', 'H', 'O', 'H', 'H'],
                                dtype='object'))

    def test_reorder_molecules(self):
        mols = self._make_molecules()
        system = System(mols)
        system.bonds = np.array([[0, 1], [3, 5]])
        # Reordering
        system.reorder_molecules([1, 0, 2, 3])
        assert_eqbonds(system.bonds, [[0, 2], [3, 4]])


class TestWhere(object):
    def setup(self):
        self.s = System.from_arrays(
            type_array=['O', 'H', 'H', 'O', 'H', 'H', 'O', 'H', 'H'],
            maps={('atom', 'molecule'): [0, 0, 0, 1, 1, 1, 2, 2, 2]})

    def teardown(self):
        pass

    def test_molecule(self):
        idx = self.s.where(molecule_index=[0, 2])
        assert_npequal(idx['atom'], [True, True, True, False, False, False,
                                     True, True, True])
        assert_npequal(idx['molecule'], [True, False, True])

    def test_atom_type(self):
        self.s = System.from_arrays(
            type_array=['Cl', 'Cl', 'O', 'H', 'H', 'O', 'H', 'H', 'O', 'H',
                        'H', 'Na', 'Na'],
            maps=
            {('atom', 'molecule'): [0, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 6]})

        idx = self.s.where(type_array='O')
        assert_npequal(idx['atom'],
                       [False, False, True, False, False, True, False, False,
                        True, False, False, False, False])
        assert_npequal(idx['molecule'], [False, False, True, True, True, False,
                                         False])

        self.s = System.from_arrays(
            type_array=['Cl', 'Cl', 'O', 'H', 'H', 'O', 'H', 'H', 'O', 'H',
                        'H', 'Na', 'Na'],
            maps=
            {('atom', 'molecule'): [0, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 6]})

        idx = self.s.where(type_array=['Na', 'Cl'])
        assert_npequal(idx['atom'],
                       [True, True, False, False, False, False, False, False,
                        False, False, False, True, True])


def test_crystal():
    '''Building a crystal by using spacegroup module'''
    na = Molecule([Atom('Na', [0.0, 0.0, 0.0])])
    cl = Molecule([Atom('Cl', [0.0, 0.0, 0.0])])

    # Fract position of Na and Cl, space group 255
    tsys = crystal([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]],
                   [na, cl],
                   225,
                   repetitions=[13, 13, 13])
    eq_(tsys.r_array.min(), 0.0)
    eq_(tsys.r_array.max(), 12.5)


def test_sort():
    na = Molecule([Atom('Na', [0.0, 0.0, 0.0])])
    cl = Molecule([Atom('Cl', [0.0, 0.0, 0.0])])

    # Fract position of Na and Cl, space group 255
    tsys = crystal([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]],
                   [na, cl],
                   225,
                   repetitions=[3, 3, 3])

    tsys.sort()
    assert_npequal(tsys.type_array[:tsys.n_mol // 2], ['Cl'] * (tsys.n_mol // 2))


# def test_random_box():
#     na = Molecule([Atom('Na', [0.0, 0.0, 0.0])])
#     cl = Molecule([Atom('Cl', [0.0, 0.0, 0.0])])
#     water = Molecule([Atom('O', [0.0, 0.0, 0.0]),
#                       Atom('H', [0.0, 0.1, 0.0]),
#                       Atom('H', [0.1, 0.0, 0.0]), ])
# 
#     box = random_box([na, cl, water],
#                      total=200,
#                      proportions=[0.1, 0.1, 0.8],
#                      size=[3, 3, 3])
# 
#     from chemlab.utils.pbc import periodic_distance
#     for a, b in [('O', 'Na'), ('O', 'Cl'), ('Na', 'Cl')]:
#         asys = box.sub(atom_type=a)
#         bsys = box.sub(atom_type=b)
# 
#         D = periodic_distance(asys.r_array[None, :], bsys.r_array[:, None], 
#                               np.array([3, 3, 3]))
# 
#         ok_(D.min() > vdw_radius(a) + vdw_radius(b))


def test_random_lattice():
    '''Testing random made box'''
    na = Molecule([Atom('Na', [0.0, 0.0, 0.0])])
    cl = Molecule([Atom('Cl', [0.0, 0.0, 0.0])])
    wat = Molecule.from_arrays(type_array=['O', 'H', 'H'])

    s = random_lattice_box([na, cl, wat], [160, 160, 160], [4, 4, 4])
    eq_(s.dimensions['molecule'], 160 * 3)
    eq_(s.dimensions['atom'], 160 * 5)


def test_bonds():
    # TODO: deprecate this shit
    from chemlab.io import datafile
    bz = datafile("tests/data/benzene.mol").read('molecule')
    na = Molecule([Atom('O', [0.0, 0.0, 0.0]),
                   Atom('H', [0.0, 0.0, 0.0]),
                   Atom('H', [0.0, 0.0, 0.0]), ])

    # Adding bonds
    s = System()
    with s.batch() as b:
        b.append(bz)

    assert_npequal(s.bonds, bz.bonds)
    assert_npequal(bz.bond_orders, [1, 2, 2, 1, 1, 2])
    assert_npequal(s.bond_orders, bz.bond_orders)

    s.add(bz)
    assert_npequal(s.type_array, ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C',
                                  'C', 'C', 'C'])
    eq_(s.dimensions['atom'], 12)
    assert_npequal(s.bonds, np.concatenate((bz.bonds, bz.bonds + 7)))

    # Reordering
    s.bonds = np.array([[0, 1], [6, 8]])
    s.reorder_molecules([1, 0])
    assert_eqbonds(s.bonds, np.array([[6, 7], [0, 2]]))

    # Selection
    ss = subsystem_from_molecules(s, [1])
    assert_npequal(ss.bonds, np.array([[0, 1]]))


def test_bond_orders():
    # Get a molecule with some bonds
    wat = _make_water()
    wat_o = wat.copy()
    # 0,1 0,2
    assert_npequal(wat.bond_orders, np.array([0, 0]))

    # Remove a bond
    wat.bonds = np.array([[0, 1]])
    assert_npequal(wat.bond_orders, np.array([0]))

    wat.bond_orders = np.array([2])

    # Try with a system
    s = System()

    s.add(wat_o)
    s.add(wat)

    assert_npequal(s.bond_orders, np.array([0, 0, 2]))
    s.reorder_molecules([1, 0])
    # Bonds get sorted accordingly
    assert_npequal(s.bond_orders, np.array([2, 0, 0]))

    s.bonds = np.array([[0, 1], [0, 2], [3, 4], [3, 5]])
    assert_npequal(s.bond_orders, np.array([2, 0, 0, 0]))
        
def test_residue():
    
    m = Molecule.from_arrays(type_array=['H', 'H', 'H', 'O', 'O'], 
                             residue_name=['VAL', 'ALA'],
                             maps={('atom', 'residue'): [0, 0, 0, 1, 1]})
    assert_npequal(m.sub(residue_index=0).type_array, ['H', 'H', 'H'])
    
    s = System([m, m])
    assert_npequal(s.maps['atom', 'residue'].value, [0, 0, 0, 1, 1, 2, 2, 2, 3, 3])

def test_query():
    type_array = ['Cl', 'Cl', 'O', 'H', 'H', 'O', 'H', 'H', 'Na', 'Na']
    maps = {('atom', 'molecule'): [0, 1, 2, 2, 2, 3, 3, 3, 4, 5]}
    s = System.from_arrays(type_array = type_array, maps=maps)
    
    assert_npequal(s.where(type_array=['Na', 'Cl'])['atom'], 
              [True, True, False, False, False, False, False, False, True, True])
    
    assert_npequal(s.where(type_array='Cl')['atom'], 
              [True, True, False, False, False, False, False, False, False, False])
    
    # We move the Cl away
    cl = s.where(type_array='Cl')['atom']
    s.r_array[cl.nonzero()[0]] = [1, 0, 0]
    s.box_vectors = np.diag([3, 3, 3])
    
    assert_npequal(s.where(type_array=['H', 'O'], within_of=(0.2, [8, 9]))['atom'],
             [False, False, True, True, True, True, True, True, False, False])

    assert_npequal(s.where(type_array=['H', 'O'], within_of=(0.2, 8))['atom'],
             [False, False, True, True, True, True, True, True, False, False])

    assert_npequal(s.where(type_array=['H', 'O'], within_of=(0.2, [8]))['atom'],
             [False, False, True, True, True, True, True, True, False, False])
    

def test_serialization():
    cl = Molecule([Atom.from_fields(type='Cl', r=[0.0, 0.0, 0.0])])
    jsonstr = cl.to_json()
    m = Molecule.from_json(jsonstr)
    eq_(Molecule.from_json(jsonstr).to_json(), jsonstr)

    na = Molecule([Atom('Na', [0.0, 0.0, 0.0])])
    cl = Molecule([Atom('Cl', [0.0, 0.0, 0.0])])

    # Fract position of Na and Cl, space group 255
    tsys = crystal([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]],
                   [na, cl],
                   225,
                   repetitions=[3, 3, 3])
    jsonstr = tsys.to_json()

    npeq_(System.from_json(jsonstr).r_array, tsys.r_array)
