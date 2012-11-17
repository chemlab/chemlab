#import hdf5
import os

def Trajectory(object):
    def __init__(self, filename):
        self.hdf = hdf5.File(filename)
        
    def _read_sys(self, index):
        atom_types = self.hdf["atoms"] 
        coords = self.hdf["coords"]
        return System.from_type_coords(zip(atom_types, coords))
            
    def last(self):
        return self._read_sys(-1)
def make_trajectory(first, filename):
    if os.path.exists(filename):
        # Restarting
        t = Trajectory(filename)
    else:
        t = Trajectory(filename, restart=False)
    return t

def test_1():

    traj = make_trajectory(MonatomicSystem(), "traj.h5", restart = True)

    for i in range(10):
        sys = traj.last()
        sys.rarray += 1.0
        traj.append(sys)
        
    

def test_2():
    traj = read_trajectory("traj.h5")
    display_trajectory(traj)

def test_gromacs():
    '''Test reading a gromacs file'''
    from chemlab.io.gro import parse_gro
    import pyglet
    pyglet.options['vsync'] = False
    from chemlab.graphics import display_system
    
    display_system(parse_gro("tests/data/water_nacl.gro"))
