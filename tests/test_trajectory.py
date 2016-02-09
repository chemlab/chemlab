from __future__ import print_function

import numpy as np

from .testtools import npeq_

from chemlab.core import Trajectory, System

np.random.seed(42)

def test_init():    
    coords = [np.random.rand(10, 3) for i in range(10)]
    t = np.arange(0, 10, 0.1)
    
    traj = Trajectory(coords, t)
    npeq_(traj.at(1)["coords"], coords[1]) 


def test_attributes():
    coords = [np.random.rand(10, 3) for i in range(10)]
    t = np.arange(0, 10, 0.1)
    traj = Trajectory(coords, t)
    system = System.from_arrays(r_array=coords[0])
    
    system.update(traj.at(1))    
    npeq_(system.r_array, coords[1])
     
def test_map():
    coords = [np.random.rand(10, 3) for i in range(10)]
    t = np.arange(0, 10, 0.1)
    traj = Trajectory(coords, t)
    
    summed_coords = traj.map(np.sum, attributes="coords")

def test_offload():
    from chemlab.io import datafile

    # We offload and retrieve a dask array
    traj = datafile("tests/data/trajout.xtc").read("trajectory", rootdir="ds")
    
# class DataStore:
#     
#     def __init__(self, rootdir):
#         self.rootdir = rootdir
#         if not os.exists(rootdir):
#             os.mkdir(rootdir)
#     
#     def __setitem__(self, attr, value):
#         bcolz.open()
# 
#     
# def test_out_of_core():
#     ds = DataStore("data/")
#     ds['coords'] = np.random.rand(10, 100, 3)
#     old = ds['coords'][0, 0, 0]
#     ds['coords'][0, 0, 0] = old + 1
    
    
    
    # ds.empty("bond_orders", 10, 100)
    
    
