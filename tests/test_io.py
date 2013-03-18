from chemlab.core import System, Atom, Molecule
from chemlab.io import DataFile
from chemlab.io.gro import GromacsIO
    
def test_datafile():
    DataFile.add_handler(GromacsIO, 'gro', '.gro')
    df = DataFile("tests/data/cry.gro") # It guesses 
    sys = df.read("system")
    assert sys.n_atoms == 1728

def test_read_gromacs():
    '''Test reading a gromacs file'''
    from chemlab.io.gro import parse_gro
    from chemlab.graphics import display_system
    parse_gro("tests/data/cry.gro")


def test_pdb():
    df = DataFile('tests/data/3ZJE.pdb')
    s = df.read('system')
    
    from chemlab.graphics import display_system
    display_system(s)
    
def test_write_gromacs():
    water = Molecule([Atom('O', [0.0, 0.0, 0.0], export={'grotype': 'OW'}),
                      Atom('H', [0.1, 0.0, 0.0], export={'grotype': 'HW1'}),
                      Atom('H', [-0.03333, 0.09428, 0.0], export={'grotype': 'HW2'})],
                      export={'groname': 'SOL'})

    sys = System.empty(200, 3*200, boxsize = 2.0)
    for i in range(200):
        sys.add(water.copy())
    
    write_gro(sys, '/tmp/dummy.gro')
