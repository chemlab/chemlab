'''This file is useful to test for conservation of various physical quantities'''

from chemlab import MonatomicSystem
from chemlab.graphics import display_system
from chemlab.molsim.integrators import evolve_generator
from chemlab.molsim import cenergy
from chemlab.db.masses import typetomass
import pylab as pl
import pyglet; pyglet.options['vsync'] = False

def test_canonical():
    '''test for Canonical Ensemble'''
    # Liquid argon Near experimental density
    sys = MonatomicSystem.spaced_lattice('Ar', 100, 5.0) 
    
    energies = []
    pot = []
    kin = []
    times = []
    
    display_system(sys)
    gen = evolve_generator(sys, 100.0, 0.002)

    count = 0
    
    for sys, t in gen:
        v = cenergy.lennard_jones(sys.r_array*1e-9, sys.type, periodic=sys.boxsize*1e-9)
        
        m = typetomass['Ar'] * 1.660538921e-27
        k = (0.5 * m * sys.varray * sys.varray * 1e6).sum()
        
        count +=1
        if (count % 1000) == 0:
            pot.append(v)
            kin.append(k)
            energies.append((v + k))
            times.append(t)
    
    display_system(sys)
    pl.plot(times, energies, label="H")
    pl.plot(times, pot, label='V')
    pl.plot(times, kin, label='K')
    pl.legend()
    pl.show()
    