from chemlab.viewer.world import Widget2
from chemlab.viewer.viewer import Viewer2
from chemlab import Atom, Molecule
import chemlab as cl
import pyglet

def test_1():
    v = Viewer2()
    mol = cl.readgeom("tests/data/tink.xyz", format="tinkerxyz")
    m = Molecule([Atom("C", (0.0, 0.0, 1.0)),
                 Atom("C", (0.0, 1.0, 0.0)),
                 Atom("H", (1.0, 0.0, 0.0)),
                 Atom("O", (1.0, 1.0, 1.0))])
    v.molecule = mol
    pyglet.app.run()
