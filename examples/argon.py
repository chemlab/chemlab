import pyglet
pyglet.options['vsync'] = False
from chemlab.core.system import MonatomicSystem
from chemlab.data import masses
from chemlab.molsim import cforces, integrators, cenergy
import pylab as pl


def evolve(sys, t, tstep, periodic, callback=None):
    
    steps = int(t/tstep)
    m = masses.typetomass[sys.type] * 1.660538921e-27 # Mass in Kg
    
    for i in range(steps):
        
        # It SHOULD be in joule
        if callback != None:
            callback(sys, i*tstep)
        farray = cforces.lennard_jones(sys.rarray, sys.type, periodic=sys.boxsize)
        
        sys.rarray, sys.varray = integrators.euler(sys.rarray, sys.varray, farray/m, tstep)
        
        # Add more periodic conditions
        rarray = sys.rarray
        if periodic:
            i_toopositive = rarray > boxsize * 0.5
            rarray[i_toopositive] -= boxsize  
            i_toonegative = rarray < - boxsize * 0.5
            rarray[i_toonegative] += boxsize
        
        sys.rarray = rarray
    return sys

def evolve_generator(sys, t, tstep, periodic):
    steps = int(t/tstep)
    m = masses.typetomass[sys.type] * 1.660538921e-27 # Mass in Kg
    boxsize = sys.boxsize
    
    for i in range(steps):
        yield sys, tstep*i        
        
        farray = cforces.lennard_jones(sys.rarray, sys.type, periodic=sys.boxsize)        
        sys.rarray, sys.varray = integrators.euler(sys.rarray, sys.varray, farray/m, tstep)
        
        # Add more periodic conditions
        rarray = sys.rarray
        if periodic:
            i_toopositive = rarray > boxsize * 0.5
            rarray[i_toopositive] -= boxsize  
            i_toonegative = rarray < - boxsize * 0.5
            rarray[i_toonegative] += boxsize
        
        sys.rarray = rarray

    
    
import pyglet

def display_system(sys):

    from chemlab.graphics.viewer import Viewer
    from chemlab.graphics.renderers import CubeRenderer, SphereRenderer
    
    v = Viewer()
    
    v.add_renderer(CubeRenderer, sys.boxsize*1e9)
    v.add_renderer(SphereRenderer, sys.atoms)
    import time
    #pyglet.clock.schedule(lambda dt: time.sleep(1/120.0)) # UGLY bugfix
    #
    #pyglet.app.run()
    
def kinetic(varray, m):
    return (0.5*m*varray**2).sum()
    
    
vens = []
kens = []
energies = []
times = []

def callback(sys, t):
    en = cenergy.lennard_jones(sys.rarray, sys.type, periodic=sys.boxsize)
    m = masses.typetomass[sys.type] * 1.660538921e-27 # Mass in Kg
    k = kinetic(sys.varray, m)
    print "Potential", en, "Kinetic", k
    vens.append(en)
    kens.append(k)
    energies.append(en+k)
    times.append(t)

import numpy as np
# Chemlab uses all SI units
sys = MonatomicSystem.random("Ar", 500, 30e-9)
sys.varray = (np.random.rand(sys.n, 3).astype(np.float32) - 0.5) * 1000 

from chemlab.graphics.viewer import Viewer
from chemlab.graphics.renderers import CubeRenderer, SphereRenderer
v = Viewer()
v.add_renderer(CubeRenderer, sys.boxsize*1e9)
sr = v.add_renderer(SphereRenderer, sys.atoms)

gen = evolve_generator(sys, t=1e-9, tstep=5e-15, periodic=True)

def update(t):
    sys, t = gen.next()
    callback(sys, t)
    sr.update(sys.rarray * 1e9)

pyglet.clock.schedule(update)
pyglet.app.run()

pl.plot(times[3:], kens[3:])
pl.plot(times[3:], vens[3:])
pl.plot(times[3:], energies[3:])

pl.show()