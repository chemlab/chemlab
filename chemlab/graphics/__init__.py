from .qtviewer import QtViewer
from .renderers import AtomRenderer, CubeRenderer
from .ui import SliderUI

def display_system(sys):
    v = QtViewer()
    sr = v.add_renderer(AtomRenderer, sys, backend='impostor')
    v.add_renderer(CubeRenderer, sys.boxsize)
    
    v.run()
    
def display_trajectory(tr):
    v = QtViewer()
    sr = v.add_renderer(AtomRenderer, tr[0].atoms, backend='impostor')
    br = v.add_renderer(CubeRenderer, tr[0].boxsize)
    
    slider = v.add_ui(SliderUI, len(tr), 100, 100, 500, 20)
    
    @slider.event
    def on_update(frame):
        sys = tr[frame]
        sr.update_positions(sys.r_array)
        br.update(sys.boxsize)

    v.run()