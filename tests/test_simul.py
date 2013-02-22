import pyglet
pyglet.options['vsync'] = False
pyglet.options['shadow_window'] = False
from chemlab import Atom, Molecule, display
from chemlab.molsim import integrators, forces
from chemlab.molsim import cforces as forces
from chemlab.graphics.viewer import Viewer
import numpy as np
import time
import multiprocessing as mp
import threading
from chemlab.core.system import MonatomicSystem
from chemlab.graphics.renderers import SphereRenderer, CubeRenderer, PointRenderer
from chemlab.molsim.analysis import pair_correlation
import pylab as pl


def test_1():
    boxsize = 50.0
    sys = MonatomicSystem.random("Ne",500, boxsize)
    #x, y = pair_correlation(sys, 20)
    #pl.plot(x, y)
    for i in range(1000):
        print "Step ", i
        farray = forces.lennard_jones(sys.r_array, "Ne", periodic=boxsize)
        # Just this time let's assume masses are 1
        sys.r_array, sys.varray = integrators.euler(sys.r_array, sys.varray, farray/300.17, 0.011)
        
        # Add more periodic conditions
        rarray = sys.r_array
        
        i_toopositive = rarray > boxsize * 0.5
        rarray[i_toopositive] -= boxsize  
        i_toonegative = rarray < - boxsize * 0.5
        rarray[i_toonegative] += boxsize
        
        sys.r_array = rarray

    #x, y = pair_correlation(sys, 20)
    #pl.plot(x, y)
    
    #pl.show()

from chemlab.molsim.integrators import evolve_generator
def test_2():
    boxsize = 15.0 #nm
    nmol = 400
    sys = MonatomicSystem.random("Ar", nmol, boxsize)
    
    v = Viewer()
    pr = v.add_renderer(SphereRenderer, sys.atoms)
    v.add_renderer(CubeRenderer, boxsize)
    
    sys.varray = (np.random.rand(nmol, 3).astype(np.float32) - 0.5)
    
    gen = evolve_generator(sys, t=1000, tstep=0.002, periodic=True)
    
    def iterate(dt):
        for i in range(10):
            sys, t = gen.next()
        pr.update(sys.r_array)
    
    import pyglet
    pyglet.clock.schedule(iterate)
    pyglet.app.run()



def test_3():
    '''Make this much more interactive'''
    from chemlab.graphics.processviewer import ProcessViewer
    boxsize = 30.0
    nmol = 1000
    sys = MonatomicSystem.random("Ar", nmol, boxsize)
    v = ProcessViewer()
    pr = v.add_renderer(SphereRenderer, sys.atoms)
    v.add_renderer(CubeRenderer, boxsize)
    
    for i in range(100):
        # Let's try to make periodic boundary conditions
        farray = forces.lennard_jones(sys.r_array, "Ar", periodic=boxsize)
        # Just this time let's assume masses are 1
        sys.r_array, sys.varray = integrators.euler(sys.r_array, sys.varray, farray/30.17, 0.01)
        
        # Add more periodic conditions
        rarray = sys.r_array
        
        i_toopositive = rarray > boxsize * 0.5
        rarray[i_toopositive] -= boxsize  
        i_toonegative = rarray < - boxsize * 0.5
        rarray[i_toonegative] += boxsize
        
        sys.r_array = rarray
        pr.update(rarray)
    
    v._p.join()
    

if __name__ == '__main__':
    test_3()
