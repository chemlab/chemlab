'''Tests for background viewer'''

def test_1():
    v = ProcessViewer()
    v.add_renderer("rend", Renderer())
    r.update("rend", args)
    
def test_2():
    v = ProcessViewer()
    sph = v.add_renderer("sphere")
    sph.update()

from chemlab.viewer import renderers
from chemlab.viewer.viewer import ProcessViewer


def test_3():
    '''This is the best solution'''
    v = ProcessViewer()
    
    rend = v.add_renderer(renderers.CubeRenderer, 10)
    rend.hello()
    #rend.update(arg)
    
