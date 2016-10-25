"""This module abstracts away the qt stuff"""
import numpy as np

from .qtviewer import QtViewer
from .qchemlabwidget import QChemlabWidget
from .qttrajectory import QtTrajectoryViewer, format_time
from ..camera import Camera

from ..renderers import AtomRenderer, BoxRenderer, BallAndStickRenderer
from ..uis import TextUI
from ..postprocessing import FXAAEffect, SSAOEffect, GammaCorrectionEffect

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
    v.run()


def display_system(sys, style='vdw'):
    '''Display the system *sys* with the default viewer.

    '''
    
    v = QtViewer()

    #v.add_post_processing(FXAAEffect)
    v.add_post_processing(SSAOEffect)    
    
    if style == 'vdw':
        sr = v.add_renderer(AtomRenderer, sys.r_array, sys.type_array,
                            backend='impostors')
    if style == 'ball-and-stick':
        sr = v.add_renderer(BallAndStickRenderer,
                            sys.r_array,
                            sys.type_array,
                            sys.bonds)
    
    if sys.box_vectors is not None:
        v.add_renderer(BoxRenderer, sys.box_vectors)
        
        # We autozoom on the box
        a, b, c = sys.box_vectors
        box_vertices = np.array([[0.0, 0.0, 0.0],
                                 a, b, c,
                                 a + b, a + c, b + c,
                                 a + b + c])
        v.widget.camera.autozoom(box_vertices)
    else:
        v.widget.camera.autozoom(sys.r_array)
    
    v.run()

def display_trajectory(sys, times, coords_list, box_vectors=None,
                       style='spheres'):
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
    
    v.add_post_processing(SSAOEffect)
    v.add_post_processing(FXAAEffect)
    v.add_post_processing(GammaCorrectionEffect, 1.60)
    
    if style == 'spheres':
        backend = 'impostors'
    elif style == 'points':
        backend = 'points'
    else:
        raise Exception("No such style")
        
    sr = v.add_renderer(AtomRenderer, sys.r_array, sys.type_array,
                        backend=backend)

    
    if sys.box_vectors is not None:
        br = v.add_renderer(BoxRenderer, sys.box_vectors)
        # We autozoom on the box
        a, b, c = sys.box_vectors
        box_vertices = np.array([[0.0, 0.0, 0.0],
                                 a, b, c,
                                 a + b, a + c, b + c,
                                 a + b + c])
        v.widget.camera.autozoom(box_vertices)
    else:
        v.widget.camera.autozoom(sys.r_array)

    
    v.set_ticks(len(coords_list))
    @v.update_function
    def on_update(index):
        sr.update_positions(coords_list[index])
        if box_vectors is not None:
            br.update(box_vectors[index])
        v.set_text(format_time(times[index]))
        v.widget.repaint()

    v.run()
