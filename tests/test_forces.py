'''Calculate forces between atoms'''

from chemlab import Atom, Molecule
from chemlab.core.system import MonatomicSystem
from chemlab.forces import forces_lj
import numpy as np

from chemlab.viewer.viewer import Viewer
from chemlab.viewer.renderers import ForcesRenderer, SphereRenderer

def test_1():
    a = Atom("Ne", [-1.0, 0.0, 0.0])
    b = Atom("Ne", [1.0, 0.0, 0.0])
    am = Molecule([a, b])
    # Force vector exterted on the first atom TODO, for optimization
    # purposes, this function should not take atom objects but coords.
    f = lennard_jones(a, b)


def test_2():
    a = Atom("Ne", [ 1, 1, 0])
    b = Atom("Ne", [ 1,-1, 0])
    c = Atom("Ne", [-1,-1, 0])
    d = Atom("Ne", [-1, 1, 0])
    sys = MonatomicSystem([a,b,c,d])
    sys = MonatomicSystem.random("Ne", 8, 7)
    farray = forces_lj(sys.atoms)
    
    v = Viewer()
    v.add_renderer(ForcesRenderer(farray*10000/3, sys.atoms))
    v.add_renderer(SphereRenderer(sys.atoms))
    
    import pyglet; pyglet.app.run()
    
