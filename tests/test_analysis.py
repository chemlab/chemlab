'''Trajectory analysis utils

'''
from __future__ import division
import numpy as np
from chemlab.core.spacegroup.crystal import crystal
from chemlab.molsim.analysis import radial_distribution_function
from chemlab.data import moldb
from chemlab.io import datafile
from chemlab.graphics import display_system

from pylab import *


def test_rdf():
    system = datafile("examples/gromacs_tutorial/confout.gro").read('system')
    # Fix for this particular system water.gro
    #system.r_array += system.box_vectors[0,0]/2
    
    gro_rdf = np.loadtxt("examples/gromacs_tutorial/rdf.xvg", skiprows=13,unpack=True)
    nbins = len(gro_rdf[0])
    
    size = system.box_vectors[0,0]/2
    
    rdfs = []
    t, coords = datafile("examples/gromacs_tutorial/traj.xtc").read("trajectory")
    i = 0
    for r_array in coords:
        rdf = radial_distribution_function(r_array,
                                           r_array, nbins*2, cutoff=size*0.99,
                                           periodic = system.box_vectors)
        rdfs.append(rdf[1])
        print "frame ", i
        i += 1
    
    rdf_avg = np.sum(rdfs, axis=0)/len(rdfs)
    print len(rdf[0])
    print len(rdf_avg)
    plot(rdf[0], rdf_avg, 'blue')
    plot(gro_rdf[0], gro_rdf[1], color='red')
    
    #show()