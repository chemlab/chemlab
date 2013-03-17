from chemlab.core.system import System
from chemlab.core.molecule import Atom, Molecule
#from chemlab.io.trajectory import make_trajectory
from chemlab.io.gro import write_gro
    
def _test_traj():
    sys = MonatomicSystem.random("Ar", 64, 1.0)
    traj = make_trajectory(sys,  "traj.hdf", restart=True)
    
    for i in range(1000):
        sys.r_array += 1
        traj.append(sys)

    print traj.npoints
    #print traj._read_sys(0).r_array
    #print traj._read_sys(1).r_array

def test_gromacs():
    '''Test reading a gromacs file'''
    from chemlab.io.gro import parse_gro
    from chemlab.graphics import display_system
    parse_gro("tests/data/cry.gro")


def test_write_gromacs():
    water = Molecule([Atom('O', [0.0, 0.0, 0.0], export={'grotype': 'OW'}),
                      Atom('H', [0.1, 0.0, 0.0], export={'grotype': 'HW1'}),
                      Atom('H', [-0.03333, 0.09428, 0.0], export={'grotype': 'HW2'})],
                      export={'groname': 'SOL'})

    sys = System.empty(200, 3*200, boxsize = 2.0)
    for i in range(200):
        sys.add(water.copy())
    
    write_gro(sys, '/tmp/dummy.gro')
    
    