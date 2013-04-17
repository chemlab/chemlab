'''Calculate forces between atoms'''

from chemlab import Atom, Molecule
from chemlab.core.system import MonatomicSystem
from chemlab.molsim.cforces import lennard_jones
from chemlab.molsim import cforces
import numpy as np

from chemlab.graphics.viewer import Viewer
from chemlab.graphics.renderers import ForcesRenderer, SphereRenderer, CubeRenderer
from chemlab.molsim.integrators import evolve_generator

def test_1():
    a = Atom("Ne", [-1.0, 0.0, 0.0])
    b = Atom("Ne", [1.0, 0.0, 0.0])
    am = Molecule([a, b])
    # Force vector exterted on the first atom TODO, for optimization
    # purposes, this function should not take atom objects but coords.
    f = lennard_jones(a, b)


def test_4atoms():
    a = Atom("Ar", [ 0.5, 0.5, 0])
    b = Atom("Ar", [ 0.5,-0.5, 0])
    c = Atom("Ar", [-0.2,-0.5, 0])
    d = Atom("Ar", [-0.5, 0.5, 0.5])
    sys = MonatomicSystem([a,b,c,d], 6.0)
    
    v = Viewer()
    sr = v.add_renderer(SphereRenderer, sys.atoms)
    v.add_renderer(CubeRenderer, sys.boxsize)
    
    # evo takes times in picoseconds
    evo = evolve_generator(sys, t=1e3, tstep=0.002, periodic=True)
    
    
    def update_pos():
        try:
            for i in range(100):
                sys, t = evo.next()
            sr.update(sys.r_array)
            
        except StopIteration:
            pass
            #import pylab as pl
            #pl.plot(distances, pitentials, 'o')
            #pl.show()


        
    v.schedule(update_pos)
    v.run()

    
from chemlab.molsim import cenergy

def test_forces():
    '''This test simply shows two atoms that are subject to a lennard
    jones potential. you can modulate the distance between atoms and
    see if this physically makes sense. For example two atoms at a
    distance of about 1.5sigma should bounce.

    '''
    import pyglet
    pyglet.options['vsync'] = False
    
    # Let's say we have to store this in nm and picoseconds
    # I setup argon atoms pretty overlapping
    a = Atom("Ar", [ 0.0, 0.0, 0.0])
    b = Atom("Ar", [ 1.00, 0.0, 0.0])
    sys = MonatomicSystem([a,b], 3.0)
    
    v = Viewer()
    
    sr = v.add_renderer(SphereRenderer, sys.atoms)
    v.add_renderer(CubeRenderer, sys.boxsize)
    
    # evo takes times in picoseconds
    evo = evolve_generator(sys, t=1e2, tstep=0.002, periodic=False)
    distances = [np.linalg.norm(sys.r_array[0] - sys.r_array[1])]
    pitentials = [cenergy.lennard_jones( sys.r_array * 1e-9, 'Ar', periodic=False)]
    
    def update_pos():
        try:
            for i in range(100):
                sys, t = evo.next()
                
            dist = np.linalg.norm(sys.r_array[0] - sys.r_array[1])
            pot = cenergy.lennard_jones( sys.r_array * 1e-9, 'Ar', periodic=False)            
            distances.append(dist)
            pitentials.append(pot)
            sr.update(sys.r_array)
            
        except StopIteration:
            import pylab as pl
            pl.plot(distances, pitentials, 'o')
            pl.show()


        
    v.schedule(update_pos)
    v.run()

from chemlab.db import lj

def test_energy():
    '''This is made as a test to verify is the potential produced is
    correct by using correct units and whatever.

    '''
    arr = np.array([[0.0, 0.0, 0.0], [0.30e-9, 0.0, 0.0]])
    
    rs = []
    ens = []
    myens = []
    forces = []
    myforces = []
    
    eps, sigma = lj.typetolj['Ar']

    for i in range(200):
        rs.append(arr[1,0])
        ens.append(cenergy.lennard_jones(arr, 'Ar', periodic=False))
        
        
        force = cforces.lennard_jones(arr, 'Ar', periodic=False)[0,0]
        forces.append(force*1e-32)
        
        sonr = sigma/arr[1,0]
        r = arr[1,0]
        #print sonr**12, sonr**6  
        
        myen = 4*eps*(sonr)**12 - 4*eps*(sonr)**6
        
        myforce = -24*eps*( 2*(sigma**12/r**13) - (sigma**6/r**7) )
        myforces.append(myforce*1e-32)
        
        myens.append(myen)
        arr[1,0] += 0.001e-9
        print force, myforce
    
    import pylab as pl
    pl.plot(rs, ens)
    pl.plot(rs, myens)
    pl.plot(rs, myforces)
    #pl.plot(rs, forces)
    pl.show()
    

def test_periodic():
    '''Now let's try to implement the periodic boundaries, we should
    try to put the molecules near the border and see if one molecule
    'passes' the wall.

    '''
    import pyglet
    pyglet.options['vsync'] = False
    
    # Let's say we have to store this in nm and picoseconds
    # I setup argon atoms pretty overlapping
    a = Atom("Ar", [ 0.5, 0.0, 0.0])
    b = Atom("Ar", [ -1.4, 0.0, 0.0])
    sys = MonatomicSystem([a,b], 3.0)
    
    v = Viewer()
    
    sr = v.add_renderer(SphereRenderer, sys.atoms)
    v.add_renderer(CubeRenderer, sys.boxsize)
    
    # evo takes times in picoseconds
    evo = evolve_generator(sys, t=1e3, tstep=0.002, periodic=True)
    
    distances = [np.linalg.norm(sys.r_array[0] - sys.r_array[1])]
    pitentials = [cenergy.lennard_jones( sys.r_array * 1e-9, 'Ar', periodic=False)]
    
    def update_pos():
        try:
            for i in range(100):
                sys, t = evo.next()
                
            dist = np.linalg.norm(sys.r_array[0] - sys.r_array[1])
            pot = cenergy.lennard_jones( sys.r_array * 1e-9, 'Ar', periodic=False)            
            distances.append(dist)
            pitentials.append(pot)
            sr.update(sys.r_array)
            
        except StopIteration:
            pass
            #import pylab as pl
            #pl.plot(distances, pitentials, 'o')
            #pl.show()


        
    v.schedule(update_pos)
    v.run()
