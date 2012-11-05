import hdf5
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

def test_3():
    sys = 
    
def display_trajectory(traj):
    v = Viewer()
    v.add_renderer(...)

