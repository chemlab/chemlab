from .viewer import Viewer
from .renderers import SphereRenderer, CubeRenderer
from .ui import SliderUI

def display_system(sys):
    v = Viewer()
    v.add_renderer(SphereRenderer, sys.atoms)
    v.add_renderer(CubeRenderer, sys.boxsize)
    v.run()
    
def display_trajectory(tr):
    v = Viewer()
    sr = v.add_renderer(SphereRenderer, tr[0].atoms)
    br = v.add_renderer(CubeRenderer, tr[0].boxsize)
    
    slider = v.add_ui(SliderUI, len(tr), 100, 100, 300, 20)
    
    @slider.event
    def on_update(frame):
        sys = tr[frame]
        sr.update(sys.rarray)
        #br.update(sys.boxsize)

    v.run()