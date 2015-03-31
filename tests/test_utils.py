'''Test for generic utils

'''
import numpy as np
from chemlab.utils.celllinkedlist import CellLinkedList
from chemlab.libs.ckdtree import cKDTree
from chemlab.utils import distance_matrix
from chemlab.utils import pbc
from chemlab.utils import geometry
from chemlab.utils import neighbors

import time
from nose_parameterized import parameterized

from numpy.random import random as nprandom

@parameterized([
    (nprandom((5, 3)) * 2, nprandom((5, 3)) * 2, 0.5),
    (nprandom((4,3)) - 0.5, nprandom((4,3)) - 0.5, 0.5) # negative nums
])
def test_distances(coords, coords_b, cutoff):
    # Consistency checks
    print "Simple"
    t = time.time()
    dist_simple = distance_matrix(coords, coords_b, cutoff, method="simple")
    print -t + time.time()

    print "Cell-lists"
    t = time.time()
    dist_clist = distance_matrix(coords, coords_b, cutoff, method="cell-lists")
    print -t + time.time()

    print dist_simple
    print dist_clist.todense()
    assert np.allclose(dist_simple, dist_clist.todense())

def test_distances_periodic():
    coords = np.array([[0.0, 0.0, 0.0],
                       [0.0, 0.9, 0.0],
                       [0.0, 0.2, 0.0]])
    coords = np.random.random((1000, 3))
    periodic = np.array([1.0, 1.0, 1.0])

    cutoff = 0.1

    # Consistency checks
    print "Simple"
    t = time.time()
    dist_simple = distance_matrix(coords, coords, cutoff, method="simple",
                                   periodic=periodic)
    print -t + time.time()

    print "Cell-lists"
    t = time.time()
    dist_clist = distance_matrix(coords, coords, cutoff,
                                  method="cell-lists", periodic=periodic)
    print -t + time.time()

    assert np.allclose(dist_simple, dist_clist.todense())


def test_pbc():
    periodic = np.array([1, 1, 1])
    coordinates = np.array([[0.1, 0.0, 0.0],
                            [1.1, 0.0, 0.0]])


    mi = pbc.minimum_image(coordinates, periodic)

    assert np.allclose(mi, np.array([[0.1, 0.0, 0.0], [0.1, 0.0, 0.0]]))

    coordinates = np.array([[0.1, 0.0, 0.0],
                            [0.9, 0.0, 0.0]])

    coordinates_nop = pbc.noperiodic(coordinates, periodic)
    assert np.allclose(mi, np.array([[0.1, 0.0, 0.0], [-0.1, 0.0, 0.0]]))

def test_geometry():

    xyz = np.array([[0.1, 0.2, 12.0],
                    [0.9, 0.0, -1.0]])
    rtp = geometry.cartesian_to_spherical(xyz)

    assert np.allclose( rtp, [[ 12.00208315, 1.10714872, 0.01863174],
                              [  1.3453624 , 0.        , 2.40877755]])

def test_neighbors():
    close = [[0.0, 0.0, 0.0],
             [0.1, 0.0, 0.0],
             [0.0, 0.1, 0.0],
             [0.0, 0.0, 0.1]]

    periodic = [1, 1, 1]

    # Testing single array
    assert neighbors.count_neighbors([0, 0, 0], close, periodic, 0.11) == 4

    ix, c = neighbors.nearest_neighbors([0, 0, 0], close, periodic, 0.11)
    assert np.allclose(ix, [0, 1, 2, 3])

    # Testing multiple arrays
    assert neighbors.count_neighbors([[0, 0, 0], [0.2, 0, 0]], close, periodic, 0.11) == [4, 1]
    ix, c = neighbors.nearest_neighbors([[0, 0, 0], [0.2, 0, 0]], close, periodic, 0.11)
    assert np.allclose(ix[0], [0, 1, 2, 3])
    assert np.allclose(ix[1], [1])

    assert np.allclose(c[0], close)
    assert np.allclose(c[1], [close[1]])
