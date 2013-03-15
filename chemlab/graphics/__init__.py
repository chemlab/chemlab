from .qtviewer import QtViewer
from .renderers import AtomRenderer, BoxRenderer
from .uis import TextUI

import numpy as np

def _system_auto_scale(sys, camera):
    # We should move the camera position and rotation in front of the 
    # center of the molecule.
    geom_center = sys.r_array.sum(axis=0) / len(sys.r_array)
    camera.position[:2] = geom_center[:2]
    camera.pivot = geom_center
    
    # Now setup the distance, that will be comparable with the size
    vectors = sys.r_array - geom_center
    sqdistances = (vectors ** 2).sum(1)[:,np.newaxis]
    sqdist = np.max(sqdistances)
    camera.position[2] = np.sqrt(sqdist) + 10.0
    

def display_system(sys, renderer='sphere'):
    v = QtViewer()
    sr = v.add_renderer(AtomRenderer, sys, backend='impostors')
    
    _system_auto_scale(sys, v.widget.camera)
    
    if sys.box_vectors is not None:
        v.add_renderer(BoxRenderer, sys.box_vectors)
    
    v.run()

def display_trajectory(sys, coords_list):
    v = QtViewer()
    sr = v.add_renderer(AtomRenderer, sys, backend='impostors')
    br = v.add_renderer(BoxRenderer, sys.box_vectors)
    
    tui = v.add_ui(TextUI, 100, 100, '')
    
    _system_auto_scale(sys, v.widget.camera)
    
    i = [0]
    def on_update():
        
        nframes = len(coords_list)
        r_array = coords_list[i[0]%nframes]
        i[0] += 1
        
        sr.update_positions(r_array)
        br.update(sys.box_vectors)
        tui.update_text("%i/%i"%(i[0]%nframes, nframes))
        
        v.widget.repaint()
    
    v.schedule(on_update, 100)
    v.run()