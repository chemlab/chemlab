from chemlab.viewer.viewer import Viewer
from chemlab.core.system import MonatomicSystem
import chemlab as cl
import pyglet
import numpy as np
from chemlab.viewer.renderers import SphereRenderer

def test_1():
    v = Viewer()
    mol = cl.readgeom("tests/data/tink.xyz", format="tinkerxyz")
    v.add_renderer(SphereRenderer(mol.atoms))
    pyglet.app.run()


def test_2():
    sys = MonatomicSystem.random("Ne", 600, 20)
    sys.bonds = []
    
    v = Viewer()
    v._camera.zoom(-20)
    
    r = SphereRenderer(sys.atoms)
    v.add_renderer(r)

    ttime = [0]
    def animate(dt, ttime=ttime):
        ttime[0] += dt
        sys.rarray -= sys.rarray*0.01*np.sin(ttime[0]*6)
        r.update()
        
    pyglet.clock.schedule_interval(animate, 1/30.0)

    pyglet.app.run()
    
if __name__ == '__main__':
    test_2()
