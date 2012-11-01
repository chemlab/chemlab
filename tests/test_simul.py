from chemlab import Atom, Molecule, display
from chemlab.molsim import integrators, forces
from chemlab.molsim import cforces as forces
from chemlab.viewer import Viewer
import numpy as np
import time
import multiprocessing as mp
import threading
from chemlab.core.system import MonatomicSystem
from chemlab.viewer.renderers import SphereRenderer, CubeRenderer
from chemlab.molsim.analysis import pair_correlation
import pylab as pl

def test_1():
    boxsize = 4.0
    sys = MonatomicSystem.random("Ne",50, boxsize)
    x, y = pair_correlation(sys, 20)
    pl.plot(x, y)
    for i in range(100):
        print "Step ", i
        farray = forces.lennard_jones(sys.rarray, "Ne", periodic=boxsize)
        # Just this time let's assume masses are 1
        sys.rarray, sys.varray = integrators.euler(sys.rarray, sys.varray, farray/300.17, 0.011)
        
        # Add more periodic conditions
        rarray = sys.rarray
        
        i_toopositive = rarray > boxsize * 0.5
        rarray[i_toopositive] -= boxsize  
        i_toonegative = rarray < - boxsize * 0.5
        rarray[i_toonegative] += boxsize
        
        sys.rarray = rarray

    x, y = pair_correlation(sys, 20)
    pl.plot(x, y)
    
    #pl.show()
    
def test_2():
    # Let's try with threads
    boxsize = 7.0
    sys = MonatomicSystem.random("Ne", 30, boxsize)
    v = Viewer()
    v.add_renderer(SphereRenderer(sys.atoms))
    v.add_renderer(CubeRenderer(boxsize))
    
    sys.varray = np.random.rand(30, 3).astype(np.float32) - 0.5
    
    def iterate(dt):
        # Let's try to make periodic boundary conditions
        farray = forces.lennard_jones(sys.rarray, "Ne", periodic=boxsize)
        # Just this time let's assume masses are 1
        sys.rarray, sys.varray = integrators.euler(sys.rarray, sys.varray, farray/30.17, 0.01)
        
        # Add more periodic conditions
        rarray = sys.rarray
        
        i_toopositive = rarray > boxsize * 0.5
        rarray[i_toopositive] -= boxsize  
        i_toonegative = rarray < - boxsize * 0.5
        rarray[i_toonegative] += boxsize
        
        sys.rarray = rarray
        v.update()
    
    import pyglet
    pyglet.clock.schedule(iterate)
    pyglet.app.run()

