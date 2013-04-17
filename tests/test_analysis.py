'''Trajectory analysis utils

'''
from __future__ import division
import numpy as np
from chemlab.core.spacegroup.crystal import crystal
from chemlab.molsim.analysis import rdf, rdf_multi
from chemlab.db import moldb
from chemlab.io import datafile
from chemlab.graphics import display_system

from pylab import *


def test_rdf():
    #system = datafile("tests/data/rdf/cry.gro").read('system')
    # Fix for this particular system water.gro
    #system.r_array += system.box_vectors[0,0]/2
    
    gro_rdf = np.loadtxt("tests/data/rdf/rdf.xvg", skiprows=13,unpack=True)
    #nbins = len(gro_rdf[0])
    size = system.box_vectors[0,0]/2
    
    rdf=rdf(system.r_array[system.type_array == 'Cl'],
            system.r_array[system.type_array == 'Li'],
            binsize=0.002,
            cutoff=size,
            periodic = system.box_vectors)

    plot(gro_rdf[0], gro_rdf[1], color='blue')
    plot(rdf[0], rdf[1], 'red')
    
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
