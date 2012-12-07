import h5py
from chemlab.core.system import MonatomicSystem, System
from chemlab.core.molecule import Atom, Molecule
from chemlab.io.trajectory import make_trajectory
from chemlab.io.gro import write_gro, read_gro_traj
    
def test_traj():
    sys = MonatomicSystem.random("Ar", 64, 1.0)
    traj = make_trajectory(sys,  "traj.hdf", restart=True)
    
    for i in range(1000):
        sys.rarray += 1
        traj.append(sys)

    print traj.npoints
    #print traj._read_sys(0).rarray
    #print traj._read_sys(1).rarray

def test_gromacs():
    '''Test reading a gromacs file'''
    from chemlab.io.gro import parse_gro
    import pyglet
    pyglet.options['vsync'] = False
    from chemlab.graphics import display_system
    
    display_system(parse_gro("tests/data/water_nacl.gro"))


def test_write_gromacs():
    water = Molecule([Atom('O', [0.0, 0.0, 0.0], export={'grotype': 'OW'}),
                      Atom('H', [0.1, 0.0, 0.0], export={'grotype': 'HW1'}),
                      Atom('H', [-0.03333, 0.09428, 0.0], export={'grotype': 'HW2'})],
                      export={'groname': 'SOL'})

    sys = System(boxsize=1.82)
    for i in range(200):
        sys.random_add(water.copy(), min_distance=0.25, maxtries=1000)
    
    write_gro(sys, '../grostudy/mywater/dummy.gro')
    
def test_read_trajectory():
    print read_gro_traj('traj.gro')
    