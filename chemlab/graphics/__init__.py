from .viewer import Viewer
from .renderers import AtomRenderer, CubeRenderer
from .ui import SliderUI

def display_system(sys, highlight=None):
    v = Viewer()
    sr = v.add_renderer(AtomRenderer, sys)
    v.add_renderer(CubeRenderer, sys.boxsize)
    
    if highlight:
        for index in highlight:
            sr.colorlist[index] = [0, 255, 255, 255]
            sr.update_colors(sr.colorlist)

    v.run()
    
def display_trajectory(tr, highlight=None):
    v = Viewer()
    sr = v.add_renderer(AtomRenderer, tr[0].atoms)
    
    if highlight:
        for index in highlight:
            sr.colorlist[index] = [0, 255, 255, 255]
            sr.update_colors(sr.colorlist)
    
    br = v.add_renderer(CubeRenderer, tr[0].boxsize)
    
    slider = v.add_ui(SliderUI, len(tr), 100, 100, 500, 20)
    
    @slider.event
    def on_update(frame):
        sys = tr[frame]
        sr.update_positions(sys.rarray)
        br.update(sys.boxsize)

    v.run()