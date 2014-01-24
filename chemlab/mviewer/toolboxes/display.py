from chemlab.mviewer.representations import BallAndStickRepresentation
from chemlab.graphics.qttrajectory import format_time

from core import *
from chemlab.db import CirDB
from chemlab.io import datafile
db = CirDB()

def display(system):
    viewer.clear()
    viewer.add_representation(BallAndStickRepresentation, system)

    autozoom()
    viewer.update()

def autozoom():
    viewer.widget.camera.autozoom(current_system().r_array)
    viewer.update()

def download_molecule(name):
    mol = db.get('molecule', name)
    display(mol)

def load_system(name):
    mol = datafile(name).read('system')
    display(mol)

def load_molecule(name):
    mol = datafile(name).read('molecule')
    display(mol)

def load_remote_molecule(url):
    from urllib import urlretrieve
    
    filename, headers = urlretrieve(url)
    mol = datafile(filename).read('molecule')
    display(mol)
    
def load_remote_system(url):
    from urllib import urlretrieve
    
    filename, headers = urlretrieve(url)
    mol = datafile(filename).read('system')
    display(mol)

def load_remote_trajectory(url):
    from urllib import urlretrieve
    
    filename, headers = urlretrieve(url)
    load_trajectory(filename)

import bisect
def goto_time(timeval):
    i = bisect.bisect(viewer.frame_times, timeval)
    viewer.traj_controls.goto_frame(i)
    
def load_trajectory(name, skip=1):
    df = datafile(name)
    dt, coords = df.read('trajectory', skip=skip)
    boxes = df.read('boxes')
    viewer.current_traj = coords
    viewer.frame_times = dt
    
    viewer.traj_controls.set_ticks(len(dt))
    
    def update(index):
        f = coords[index]
        # update the current representation
        viewer.representation.update_positions(f)
        current_system().r_array = f
        current_system().box_vectors = boxes[index]
        viewer.traj_controls.set_time(dt[index])
        viewer.update()
    viewer.traj_controls.show()
    viewer.traj_controls.frame_changed.connect(update)
