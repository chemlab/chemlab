from .qtviewer import QtViewer
from .qchemlabwidget import QChemlabWidget
from .qttrajectory import QtTrajectoryViewer, format_time
from .renderers import AtomRenderer, BoxRenderer, BallAndStickRenderer
from .uis import TextUI

import numpy as np

def _system_auto_scale(sys, camera, offset=0.0):
    # We should move the camera position and rotation in front of the 
    # center of the molecule.
    geom_center = sys.r_array.sum(axis=0) / len(sys.r_array)
    camera.position[:2] = geom_center[:2]
    camera.pivot = geom_center
    
    # Now setup the distance, that will be comparable with the size
    vectors = sys.r_array - geom_center
    sqdistances = (vectors ** 2).sum(1)[:,np.newaxis]
    sqdist = np.max(sqdistances)
    camera.position[2] = np.sqrt(sqdist) + offset
    

def display_molecule(mol, style='ball-and-stick'):
    '''Display the molecule *mol* with the default viewer.

    '''
    v = QtViewer()
    if style == 'ball-and-stick':
        bs = v.add_renderer(BallAndStickRenderer,
                            mol.r_array,
                            mol.type_array,
                            mol.bonds)
    elif style == 'vdw':
        sr = v.add_renderer(AtomRenderer, mol.r_array, mol.type_array,
                            backend='impostors')
    else:
        raise Exception("Rendering style unknown")
    
    v.widget.camera.autozoom(mol.r_array)
    #_system_auto_scale(mol, v.widget.camera, 1.0)
    v.run()


def display_system(sys):
    '''Display the system *sys* with the default viewer.

    '''
    
    
    v = QtViewer()
    sr = v.add_renderer(AtomRenderer, sys.r_array, sys.type_array,
                        backend='impostors')
    
    #_system_auto_scale(sys, v.widget.camera, 4.0)
    v.widget.camera.autozoom(sys.r_array)
    
    if sys.box_vectors is not None:
        v.add_renderer(BoxRenderer, sys.box_vectors)
    
    v.run()

def display_trajectory(sys, times, coords_list):
    '''Display the the system *sys* and instrument the trajectory
    viewer with frames information.
    
    .. image:: /_static/display_trajectory.png
    
    **Parameters**

    sys: :py:class:`~chemlab.core.System`
        The system to be displayed
    times: np.ndarray(NFRAMES, dtype=float)
        The time corresponding to each frame. This is used
        only for feedback reasons.
    coords_list: list of np.ndarray((NFRAMES, 3), dtype=float)
        Atomic coordinates at each frame.
    
    '''
    
    v = QtTrajectoryViewer()
    sr = v.add_renderer(AtomRenderer, sys.r_array, sys.type_array,
                        backend='impostors')
    br = v.add_renderer(BoxRenderer, sys.box_vectors)
    #_system_auto_scale(sys, v.widget.camera, 4.0)
    v.widget.camera.autozoom(sys.r_array)
    
    v.set_ticks(len(coords_list))
    @v.update_function
    def on_update(index):
        sr.update_positions(coords_list[index])
        br.update(sys.box_vectors)
        v.set_text(format_time(times[index]))
        v.widget.repaint()

    v.run()