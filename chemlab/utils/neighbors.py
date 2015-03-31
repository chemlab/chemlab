''' Nearest neighbors searches utilities

@author Gabriele Lanaro <gabriele.lanaro@gmail.com>
@date 30-03-2015

'''

import numpy as np
import collections

# Our searches use mainly a periodic variant of KDTree
from ..libs.periodic_kdtree import PeriodicCKDTree

def _check_coordinates(coordinates):
    '''Validate coordinate-like input'''
    # Return numpy array
    coordinates = np.array(coordinates)
    return coordinates
def _check_periodic(periodic):
    '''Validate periodic input'''
    periodic = np.array(periodic)

    # If it is a matrix
    if len(periodic.shape) == 2:
        assert periodic.shape[0] == periodic.shape[1], 'periodic shoud be a square matrix or a flat array'
        return np.diag(periodic)
    elif len(periodic.shape) == 1:
        return periodic
    else:
        raise ValueError("periodic argument can be either a 3x3 matrix or a shape 3 array.")

def isnested(array):

    if len(array) == 0:
        return False
    elif isinstance(array[0], collections.Iterable):
        return True
    else:
        return False

def nearest_neighbors(coordinates_a, coordinates_b, periodic, r=None, n=None):
    '''Nearest neighbor search between two arrays of coordinates. Notice that
    you can control the result by selecting neighbors either by radius *r* or
    by number *n*. The algorithm uses a periodic variant of KDTree to reach a
    Nlog(N) time complexity.

    :param np.ndarray coordinates_a: Either an array of coordinates of shape (N,3)
                                     or a single point of shape (3,)
    :param np.ndarray coordinates_b: Same as coordinates_a
    :param np.ndarray periodic: Either a matrix of box vectors (3, 3) or an
                                array of box lengths of shape (3,). Only
                                orthogonal boxes are supported.
    :param float r: Radius of neighbor search
    :param int n: Number of nearest neighbors to return

    '''

    if r is None and n is None:
        raise ValueError('You should pass either the parameter n or r')
    coordinates_a = _check_coordinates(coordinates_a)
    coordinates_b = _check_coordinates(coordinates_b)
    periodic = _check_periodic(periodic)

    kdtree = PeriodicCKDTree(periodic, coordinates_b)

    if r is not None:
        neigh = kdtree.query_ball_point(coordinates_a, r)
        if isnested(neigh):
            return (neigh, [coordinates_b.take(nb, axis=0) for nb in neigh])
        else:
            return (neigh, coordinates_b.take(neigh, axis=0)) if len(neigh) != 0 else ([], [])

    if n is not None:
        neigh = kdtree.query(coordinates_b, n)
        return neigh if len(neigh) != 0 else ([], [])

def count_neighbors(coordinates_a, coordinates_b, periodic, r):
    '''Count the neighbours number of neighbors.

    :param np.ndarray coordinates_a: Either an array of coordinates of shape (N,3)
                                     or a single point of shape (3,)
    :param np.ndarray coordinates_b: Same as coordinates_a
    :param np.ndarray periodic: Either a matrix of box vectors (3, 3) or an
                                array of box lengths of shape (3,). Only
                                orthogonal boxes are supported.
    :param float r: Radius of neighbor search

    '''
    indices = nearest_neighbors(coordinates_a, coordinates_b, periodic, r=r)[0]

    if len(indices) == 0:
        return 0

    if isinstance(indices[0], collections.Iterable):
        return [len(ix) for ix in indices]
    else:
        return len(indices)
