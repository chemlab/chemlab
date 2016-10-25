'''Test for generic utils

'''
import numpy as np
# import dask.array as da
from chemlab.utils.pbc import distance_matrix, minimum_image, noperiodic
from chemlab.utils.geometry import cartesian_to_spherical
from chemlab.utils.neighbors import count_neighbors, nearest_neighbors
from chemlab.utils.numbaz import Int32HashTable
from .testtools import npeq_

import time

def test_distances_periodic():
    coords = np.array([[0.0, 0.0, 0.0],
                       [0.0, 0.9, 0.0],
                       [0.0, 0.2, 0.0]])
    coords = np.random.random((1000, 3))
    periodic = np.array([1.0, 1.0, 1.0])

    cutoff = 0.1

    # Consistency checks
    dist_simple = distance_matrix(coords, coords, periodic=periodic)
    
    # dist_dask = distance_matrix(da.from_array(coords, chunks=100), 
    #                             da.from_array(coords, chunks=100),
    #                             da.from_array(periodic, chunks=3))
    # assert np.allclose(dist_dask, dist_simple)


def test_pbc():
    periodic = np.array([1, 1, 1])
    coordinates = np.array([[0.1, 0.0, 0.0],
                            [1.1, 0.0, 0.0]])
    mi = minimum_image(coordinates, periodic)

    npeq_(mi, np.array([[0.1, 0.0, 0.0], [0.1, 0.0, 0.0]]))

    coordinates = np.array([[0.1, 0.0, 0.0],
                            [0.9, 0.0, 0.0]])

    coordinates_nop = noperiodic(coordinates, periodic)
    npeq_(coordinates_nop, np.array([[0.1, 0.0, 0.0], [-0.1, 0.0, 0.0]]))

def test_geometry():

    xyz = np.array([[0.1, 0.2, 12.0],
                    [0.9, 0.0, -1.0]])
    rtp = cartesian_to_spherical(xyz)

    npeq_(rtp,[[ 12.00208315, 1.10714872, 0.01863174],
              [  1.3453624 , 0.        , 2.40877755]])

def test_neighbors():
    close = [[0.0, 0.0, 0.0],
             [0.1, 0.0, 0.0],
             [0.0, 0.1, 0.0],
             [0.0, 0.0, 0.1]]

    periodic = [1, 1, 1]

    # Testing single array
    npeq_(count_neighbors([0, 0, 0], close, periodic, 0.11), 4)

    ix, c = nearest_neighbors([0, 0, 0], close, periodic, 0.11)
    npeq_(ix, [0, 1, 2, 3])

    # Testing multiple arrays
    npeq_(count_neighbors([[0, 0, 0], [0.2, 0, 0]], close, periodic, 0.11), [4, 1])
    
    ix, c = nearest_neighbors([[0, 0, 0], [0.2, 0, 0]], close, periodic, 0.11)
    npeq_(ix[0], [0, 1, 2, 3])
    npeq_(ix[1], [1])

    npeq_(c[0], close)
    npeq_(c[1], [close[1]])

def test_hashtable():
    
    ht = Int32HashTable(16)
    ht.push(0, 1)
    ht.push(1, 2)
    
    npeq_(ht.map(np.array([0, 1, 1, 1, 0, 0, 1])), [1, 2, 2, 2, 1, 1, 2])
