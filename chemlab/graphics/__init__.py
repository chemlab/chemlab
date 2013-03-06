from .qtviewer import QtViewer
from .renderers import AtomRenderer, BoxRenderer
from .ui import SliderUI

def display_system(sys):
    v = QtViewer()
    sr = v.add_renderer(AtomRenderer, sys, backend='impostor')
    
    if sys.box_vectors is not None:
        v.add_renderer(BoxRenderer, sys.box_vectors)
    
    v.run()
    
def display_trajectory(sys, coords_list):
    v = QtViewer()
    sr = v.add_renderer(AtomRenderer, sys, backend='impostor')
    br = v.add_renderer(BoxRenderer, sys.box_vectors)
    
    #slider = v.add_ui(SliderUI, len(tr), 100, 100, 500, 20)
    #@slider.event
    i = [0]
    def on_update():
        r_array = coords_list[i[0]%len(coords_list)]
        i[0] += 1
        sr.update_positions(r_array)
        br.update(sys.box_vectors)
        v.widget.repaint()
    v.schedule(on_update, 1000)
    v.run()