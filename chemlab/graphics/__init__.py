from .viewer import Viewer
from .renderers import SphereRenderer

def display_system(sys):
    v = Viewer()
    v.add_renderer(SphereRenderer, sys.atoms)
    v.run()