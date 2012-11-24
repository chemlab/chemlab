from .viewer import Viewer
from .renderers import SphereRenderer, CubeRenderer

def display_system(sys):
    v = Viewer()
    v.add_renderer(SphereRenderer, sys.atoms)
    v.add_renderer(CubeRenderer, sys.boxsize)
    v.run()