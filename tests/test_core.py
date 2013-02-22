"""Test core types like Molecule and Atom.

"""
from chemlab import Molecule, Atom
from chemlab.core.system import SystemFast
from chemlab.core.spacegroup.crystal import crystal
import numpy as np
import unittest

def test_init():
    """Test initialization of the Molecule and Atom classes."""
    # Default units for coordinates are Angstroms
    
    mol = Molecule([Atom("O", [-4.99, 2.49, 0.0]),
                    Atom("H", [-4.02, 2.49, 0.0]),
                    Atom("H", [-5.32, 1.98, 1.0])],[])

    """Tests the sanity of the coordinates for each atom."""
        
    #assert np.allclose(self.atoms[0].r, np.array([-4.99, 2.49, 0.0]))
    #assert np.allclose(self.atoms[1].r, np.array([-4.02, 2.49, 0.0]))
    #assert np.allclose(self.atoms[2].r, np.array([-5.32, 1.98, 0.75]))



#     def test_symbol(self):
#         """Tests the correctness of the atom symbol."""
#         symbols = ["O", "H", "H"]
#         for i, t in enumerate(self.mol.type_array):
#             assert t == symbols[i]
        
#     def test_init_array(self):
#         mol = Molecule.from_arrays(type_array = np.array(['H', 'H', 'O']),
#                                    r_array = np.zeros((3,3), dtype=np.double))
#         assert mol

    # def test_bonds(self):
    #     """Tests if the bonds are created"""
    #     print self.mol.bonds
    #     assert (self.mol.bonds[0].id_bonded == [1,2])
    #     assert (self.mol.bonds[1].id_bonded == [1,3])
       
    # def test_angles(self):
    #     """Test if the angles are created"""
    #     print self.mol.angles
        
    # def test_dihedrals(self):
    #     print self.mol.dihedrals
    #def test_formula(self):
    #    assert self.mol._det_formula() == "H2O"


def test_system():
    wat = Molecule([Atom("O", [-4.99, 2.49, 0.0]),
                    Atom("H", [-4.02, 2.49, 0.0]),
                    Atom("H", [-5.32, 1.98, 1.0])])

    wat.r_array *= 0.1
    s = SystemFast(4, 4*3)
    
    for i in xrange(s.n_mol):
        wat.r_array += 0.1
        s.add(wat)
    
    print s.r_array
    print s.m_array
    print s.type_array
    print s.mol_indices
    print s.mol_n_atoms

    print s.get_molecule(1)
    


def test_crystal():
    '''Building a crystal by using spacegroup module'''
    na = Molecule([Atom('Na', [0.0, 0.0, 0.0])])
    cl = Molecule([Atom('Cl', [0.0, 0.0, 0.0])])
    
    # Fract position of Na and Cl, space group 255
    tsys = crystal([[0.0, 0.0, 0.0],[0.5, 0.5, 0.5]], [na, cl], 225, repetitions=[13,13,13])
    
    
def test_system_lattice():
    wat = Molecule([Atom("O", [-4.99, 2.49, 0.0]),
                    Atom("H", [-4.02, 2.49, 0.0]),
                    Atom("H", [-5.32, 1.98, 1.0])])
    cl = Molecule([Atom("Cl", [0.0, 0.0, 0.0])])
    
    size = 2
    
    def generate_lattice_r():
        cell = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.0],
                         [0.5, 0.0, 0.5], [0.0, 0.5, 0.5]])
        cells = [size, size, size]
        i = 0
        for x in range(cells[0]):
            for y in range(cells[1]):
                for z in range(cells[2]):
                    for cord in cell:
                        yield i, cord
                        i += 1
    
    n_mol = size*size*size*4
    n_cl = int(n_mol * 0.3)
    n_wat = n_mol - n_cl
    print n_mol, n_wat, n_cl

    s = SystemFast(n_mol, cl.n_atoms*n_cl + wat.n_atoms*n_wat)    
    
    coord_list = []
    for i,r in generate_lattice_r():
        coord_list.append(r)
    
    import random
    
    # Shuffling stuff to accomodate gromacs
    random.shuffle(coord_list)
    for ia in range(n_wat):
        r = coord_list[ia]
        wat.r_array -= wat.geometric_center
        wat.r_array += r
        s.add(wat)

    for ib in range(n_cl):
        r = coord_list[ia + ib -1]
        cl.r_array -= cl.geometric_center
        cl.r_array += r
        s.add(cl)
    print s.type_array
        
