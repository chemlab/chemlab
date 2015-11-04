'''Test for generic utils

'''
import numpy as np
import dask.array as da
# from chemlab.utils.celllinkedlist import CellLinkedList
# from chemlab.libs.ckdtree import cKDTree
from chemlab.utils.pbc import distance_matrix
# from chemlab.utils import pbc
# from chemlab.utils import geometry
# from chemlab.utils import neighbors

import time
# from nose_parameterized import parameterized

def test_distances_periodic():
    coords = np.array([[0.0, 0.0, 0.0],
                       [0.0, 0.9, 0.0],
                       [0.0, 0.2, 0.0]])
    coords = np.random.random((1000, 3))
    periodic = np.array([1.0, 1.0, 1.0])

    cutoff = 0.1

    # Consistency checks
    dist_simple = distance_matrix(coords, coords, periodic=periodic)
    
    dist_dask = distance_matrix(da.from_array(coords, chunks=100), 
                                da.from_array(coords, chunks=100),
                                da.from_array(periodic, chunks=3))
    assert np.allclose(dist_dask, dist_simple)


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
