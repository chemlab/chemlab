from __future__ import print_function
import numpy as np

from chemlab.core import System, Atom, Molecule
from chemlab.io import datafile, add_default_handler

from chemlab.io.handlers import GromacsIO
from chemlab.io.handlers import EdrIO
from nose.tools import assert_raises, eq_
from nose.plugins.skip import SkipTest

from .testtools import assert_npequal, assert_eqbonds, assert_allclose

def test_datafile():
    df = datafile("tests/data/cry.gro") # It guesses
    sys = df.read("system")
    eq_(sys.n_atoms, 1728)
    assert_npequal(sys.type_array[:3], ['Li', 'Li', 'Li'])
    assert_npequal(sys.type_array[-3:], ['Cl', 'Cl', 'Cl'])

def test_read_pdb():
    df = datafile('tests/data/3ZJE.pdb')
    s = df.read('system')
    assert_npequal(s.type_array[:3], ['N', 'C', 'C'])

def test_read_pdb_secondary():
    system = datafile('tests/data/pdb1g8p.ent', format='pdb').read('system')
    # assert np.all(system.secondary_structure[106:109] == 'S')
    
    eq_(system.sub(secondary_id=1).residue_name[0], 'VAL')
    assert_npequal(system.sub(secondary_id=1).residue_name, ['VAL', 'VAL', 'ASP', 'LEU'])
    
    helices = system.sub(secondary_structure='H')
    helix = helices.sub(secondary_id=helices.secondary_id[0])
    assert_npequal(helix.residue_name, ['PRO', 'PHE', 'SER', 'ALA', "ILE"])
    
    

def test_write_pdb():
    water = Molecule([Atom('O', [0.0, 0.0, 0.0], export={'pdb.type': 'O'}),
                      Atom('H', [0.1, 0.0, 0.0], export={'pdb.type': 'H'}),
                      Atom('H', [-0.03333, 0.09428, 0.0], export={'pdb.type': 'H'})],
                      export={'groname': 'SOL'})

    sys = System.empty()
    with sys.batch() as b:
        for i in range(200):
            water.r_array += 0.1
            b.append(water.copy())

    df = datafile('/tmp/dummy.pdb', mode="w")
    df.write("system", sys)

def test_read_gromacs():
    '''Test reading a gromacs file'''
    df = datafile('tests/data/cry.gro')
    s = df.read('system')

def test_write_gromacs():
    water = Molecule([Atom('O', [0.0, 0.0, 0.0], name="OW"),
                      Atom('H', [0.1, 0.0, 0.0], name='HW1'),
                      Atom('H', [-0.03333, 0.09428, 0.0], name='HW2')],
                      name='SOL')

    sys = System.empty()
    with sys.batch() as b:
        for i in range(200):
            b.append(water.copy())
    sys.box_vectors = [[2, 0, 0], [0, 2, 0], [0, 0, 2]]
    
    df = datafile('/tmp/dummy.gro', mode="w")
    df.write('system', sys)

    with assert_raises(Exception):
        df = datafile('/tmp/dummy.gro')
        df.write('system', sys)

    df = datafile('/tmp/dummy.gro')
    sread = df.read('system')
    assert all(sread.type_array == sys.type_array)

def test_read_edr():
    df = datafile('tests/data/ener.edr')
    #df.read('frames')

    dt, temp = df.read('quantity', 'Temperature')
    unit = df.read('units', 'Temperature')

    try:
        df.read('quantity', 'NonExistent')
    except:
        pass

def test_read_xyz():
    df = datafile('tests/data/sulphoxide.xyz')
    mol1 = df.read('molecule')


    df = datafile('/tmp/t.xyz', mode="w")
    df.write('molecule', mol1)

    df = datafile('/tmp/t.xyz', mode="rb")
    mol2 = df.read('molecule')

    assert np.allclose(mol1.r_array, mol2.r_array)
    assert all(mol1.type_array == mol2.type_array)


def test_read_mol():
    df = datafile('tests/data/benzene.mol')
    mol1 = df.read('molecule')

def test_read_xtc():
    df = datafile('tests/data/trajout.xtc')
    traj = df.read('trajectory')

def test_read_cml():
    df = datafile('tests/data/mol.cml')
    mol = df.read("molecule")

def test_write_cml():
    df = datafile('tests/data/mol.cml')
    mol = df.read("molecule")

    df = datafile('/tmp/sadf.cml', 'w')
    df.write('molecule', mol)

def test_read_cclib():
    try:
        import cclib
    except:
        raise SkipTest
    df = datafile('tests/data/cclib/water_mp2.out', format='gamess')

    # Reading a properties that does exist
    result1 = df.read('gbasis')
    result2 = [[('S',
     [(130.7093214, 0.154328967295),
     (23.8088661, 0.535328142282),
     (6.4436083, 0.444634542185)]),
    ('S',
     [(5.0331513, -0.099967229187),
     (1.1695961, 0.399512826089),
     (0.380389, 0.70011546888)]),
    ('P',
     [(5.0331513, 0.155916274999),
     (1.1695961, 0.607683718598),
     (0.380389, 0.391957393099)])],
    [('S',
     [(3.4252509, 0.154328967295),
     (0.6239137, 0.535328142282),
     (0.1688554, 0.444634542185)])],
    [('S',
     [(3.4252509, 0.154328967295),
     (0.6239137, 0.535328142282),
     (0.1688554, 0.444634542185)])]]

    assert result1 == result2
