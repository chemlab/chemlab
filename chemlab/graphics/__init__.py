from .qtviewer import QtViewer
from .renderers import AtomRenderer, BoxRenderer
from .ui import SliderUI

import numpy as np

def display_system(sys, renderer='sphere'):
    v = QtViewer()
    sr = v.add_renderer(AtomRenderer, sys, type='impostor')
    
    # We should move the camera position and rotation in front of the 
    # center of the molecule.
    geom_center = sys.r_array.sum(axis=0) / len(sys.r_array)
    v.widget.camera.position[:2] = geom_center[:2]
    v.widget.camera.pivot = geom_center
    
    # Now setup the distance, that will be comparable with the size
    vectors = sys.r_array - geom_center
    sqdistances = (vectors ** 2).sum(1)[:,np.newaxis]
    sqdist = np.max(sqdistances)
    v.widget.camera.position[2] = sqdist
    
    if sys.box_vectors is not None:
        v.add_renderer(BoxRenderer, sys.box_vectors)
    
    v.run()
    
def display_trajectory(sys, coords_list):
    v = QtViewer()
    sr = v.add_renderer(AtomRenderer, sys, type='impostor')
    br = v.add_renderer(BoxRenderer, sys.box_vectors)
    
    i = [0]
    
    def on_update():
        
        nframes = len(coords_list)
        r_array = coords_list[i[0]%nframes]
        i[0] += 1
        
        sr.update_positions(r_array)
        br.update(sys.box_vectors)
        v.widget.repaint()
    
    v.schedule(on_update, 100)
    v.run()