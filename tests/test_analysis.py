'''Trajectory analysis utils

'''
from __future__ import division
import numpy as np
from chemlab.core.spacegroup.crystal import crystal
from chemlab.molsim.analysis import rdf, rdf_multi
from chemlab.db import ChemlabDB
from chemlab.io import datafile
from chemlab.graphics import display_system

from pylab import *

import time

class Timer(object):
    def start(self):
        self.t = time.time()
    def stop(self):
        print("Elapsed", time.time() - self.t)

timer = Timer()

def test_rdf():
    system = datafile("tests/data/rdf/cry.gro").read('system')
    # Fix for this particular system water.gro
    #system.r_array += system.box_vectors[0,0]/2
    
    gro_rdf = np.loadtxt("tests/data/rdf/rdf.xvg", skiprows=13,unpack=True)
    #nbins = len(gro_rdf[0])
    size = system.box_vectors[0,0]/2
    
    rdf_ =rdf(system.r_array[system.type_array == 'Cl'],
              system.r_array[system.type_array == 'Li'],
              binsize=0.002,
              cutoff=size,
              periodic = system.box_vectors)

    plot(gro_rdf[0], gro_rdf[1], color='blue')
    #print len(rdf_[0]), len(rdf_[1])
    plot(rdf_[0][1:], rdf_[1], 'red')
    
    show()

def test_newrdf():
    from chemlab.molsim.rdf import distance_histogram
        
    system = datafile("tests/data/rdf/cry.gro").read('system')
    #system = datafile("/home/gabriele/projects/LiCl/molfrac-0.39-48668/opt.gro").read('system')
    size = system.box_vectors[0,0]/2
    
    timer.start()
    rdf_old = rdf(system.r_array[system.type_array == 'Cl'],
                 system.r_array[system.type_array == 'Li'],
                 binsize=0.2,
                 cutoff=size,
                 periodic=system.box_vectors, normalize=False)
    timer.stop()
    
    timer.start()
    rdf_new = distance_histogram(system.r_array[system.type_array == 'Cl'],
                                 system.r_array[system.type_array == 'Li'],
                                 binsize=0.2,
                                 cutoff=size,
                                 periodic=system.box_vectors)
    timer.stop()
    1/0
    plot(rdf_new, 'r')
    plot(rdf_old[1], 'b')
    show()
    
    
def test_rdf_oxy():
    system = datafile("examples/gromacs_tutorial/confout.gro").read('system')
    # Fix for this particular system water.gro
    #system.r_array += system.box_vectors[0,0]/2
    
    gro_rdf = np.loadtxt("examples/gromacs_tutorial/rdf.xvg",
                         skiprows=13,unpack=True)
    
    #nbins = len(gro_rdf[0])
    size = system.box_vectors[0,0]/2
    
    rd=rdf(system.r_array[system.type_array == 'O'],
            system.r_array[system.type_array == 'O'],
            binsize=0.002,
            cutoff=size,
            periodic = system.box_vectors)

    plot(gro_rdf[0], gro_rdf[1], color='blue')
    plot(rd[0], rd[1], 'red')
    
    show()
    
def test_rdf_multi():
    gro_rdf = np.loadtxt("examples/gromacs_tutorial/rdf.xvg",
                         skiprows=13,unpack=True)

    syst = datafile("examples/gromacs_tutorial/confout.gro").read('system')
    df = datafile("examples/gromacs_tutorial/traj.xtc")
    t, coords = df.read("trajectory")
    boxes = df.read("boxes")

    
    rd = rdf_multi(coords[:30], coords[:30],
                   syst.type_array == 'O',
                   syst.type_array == 'O',
                   boxes)
    
    plot(gro_rdf[0], gro_rdf[1], color='blue')
    #print len(rd[0]), len(rd[1])
    plot(rd[0], rd[1], 'red')
    show()
