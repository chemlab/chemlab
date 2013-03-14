from .qtviewer import QtViewer
from .renderers import AtomRenderer, BoxRenderer
from .ui import SliderUI

def display_system(sys, renderer='sphere'):
    v = QtViewer()
    sr = v.add_renderer(AtomRenderer, sys, type='impostor')
    
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