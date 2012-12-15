from chemlab.graphics.viewer import Viewer
from chemlab.graphics.renderers import SphereImpostorRenderer

from chemlab.graphics.colors import orange, blue, forest_green
def test_1():
    v = Viewer()
    
    poslist = [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]]
    radiuslist = [0.5, 0.1, 0.5]
    colorlist = [orange, blue, forest_green]
    v.add_renderer(SphereImpostorRenderer, poslist, radiuslist, colorlist)
    
    v.run()

