from chemlab.mviewer.representations import BallAndStickRepresentation
from chemlab.graphics.qttrajectory import format_time

from .core import *
from chemlab.db import CirDB
from chemlab.io import datafile
from chemlab.core import System
import numpy as np


db = CirDB()

def display_system(system, autozoom=True):
    '''Display a `~chemlab.core.System` instance at screen'''
    viewer.clear()
    viewer.add_representation(BallAndStickRepresentation, system)

    if autozoom:
        autozoom_()
    
    viewer.update()
    msg(str(system))

def display_molecule(mol, autozoom=True):
    '''Display a `~chemlab.core.Molecule` instance in the viewer.

    This function wraps the molecule in a system before displaying
    it.

    '''
    s = System([mol])
    display_system(s, autozoom=True)

def autozoom():
    '''Find optimal camera zoom level for the current view.'''
    viewer.widget.camera.autozoom(current_system().r_array)
    viewer.update()
autozoom_ = autozoom # To prevent shadowing

def download_molecule(name):
    '''Download a molecule by name.'''
    mol = db.get('molecule', name)
    display_molecule(mol)

def load_system(name, format=None):
    '''Read a `~chemlab.core.System` from a file.

    .. seealso:: `chemlab.io.datafile`
    
    '''
    mol = datafile(name).read('system')
    display_system(mol)

def load_molecule(name, format=None):
    '''Read a `~chemlab.core.Molecule` from a file.

    .. seealso:: `chemlab.io.datafile`
    
    '''    
    mol = datafile(name, format=format).read('molecule')
    display_system(System([mol]))

def load_remote_molecule(url, format=None):
    '''Load a molecule from the remote location specified by *url*.
    
    **Example**

    ::
    
        load_remote_molecule('https://raw.github.com/chemlab/chemlab-testdata/master/benzene.mol')
    
    '''
    from urllib import urlretrieve
    
    filename, headers = urlretrieve(url)
    load_molecule(filename, format=format)
    
def load_remote_system(url, format=None):
    '''Load a system from the remote location specified by *url*.
    
    **Example**
    
    ::
    
        load_remote_system('https://raw.github.com/chemlab/chemlab-testdata/master/naclwater.gro')
    '''
    from urllib import urlretrieve
    
    filename, headers = urlretrieve(url)
    load_system(filename, format=format)

def load_remote_trajectory(url, format=None):
    '''Load a trajectory file from a remote location specified by *url*.

    .. seealso:: load_remote_system
    
    '''
    from urllib import urlretrieve
    filename, headers = urlretrieve(url)
    load_trajectory(filename, format)

def write_system(filename, format=None):
    '''Write the system currently displayed to a file.'''
    datafile(filename, format=format, mode='w').write('system',
                                                      current_system())
    
def write_molecule(filename, format=None):
    '''Write the system displayed in a file as a molecule.'''
    datafile(filename, format=format,
             mode='w').write('molecule',current_system())

import bisect

def goto_time(timeval):
    '''Go to a specific time (in nanoseconds) in the current
    trajectory.

    '''
    i = bisect.bisect(viewer.frame_times, timeval * 1000)
    goto_frame(i)
    
def goto_frame(frame):
    '''Go to a specific frame in the current trajectory.'''
    viewer.traj_controls.goto_frame(frame)

_frame_processors = []

def load_trajectory(name, skip=1, format=None):
    '''Load a trajectory file into chemlab. You should call this
    command after you load a `~chemlab.core.System` through
    load_system or load_remote_system.

    '''
    df = datafile(name, format=format)
    dt, coords = df.read('trajectory', skip=skip)
    boxes = df.read('boxes')
    viewer.current_traj = coords
    viewer.frame_times = dt
    
    viewer.traj_controls.set_ticks(len(dt))
    
    def update(index):
        
        f = coords[index]        
        
        for fp in _frame_processors:
            f = fp(coords, index)

        # update the current representation
        viewer.representation.update_positions(f)
        viewer.representation.update_box(boxes[index])
        current_system().r_array = f
        current_system().box_vectors = boxes[index]
        viewer.traj_controls.set_time(dt[index])
        viewer.update()
    
    viewer.traj_controls.show()
    viewer.traj_controls.frame_changed.connect(update)

def guess_bonds():
    '''Guess the bonds in the current system'''
    current_system().guess_bonds()
    reload_system()
    
def reload_system():
    '''Reload the current system in the viewer.'''
    return display_system(current_system(), autozoom=False)
