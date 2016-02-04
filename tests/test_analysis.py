'''Trajectory analysis utils

'''
from __future__ import division
import numpy as np
from chemlab.core.spacegroup.crystal import crystal
from chemlab.molsim.analysis import rdf, rdf_multi
from chemlab.db import ChemlabDB
from chemlab.io import datafile
from chemlab.graphics import display_system
from nose.tools import eq_

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
    
    mse = ((rdf_[1] - gro_rdf[1, :-2])**2).mean()
    assert mse < 1.0
