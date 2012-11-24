import h5py
from chemlab.core.system import MonatomicSystem
from chemlab.io.trajectory import make_trajectory
    
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

