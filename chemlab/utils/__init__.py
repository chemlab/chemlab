from __future__ import print_function
import numpy as np

from .distances import distances_within
from .distances import distance_matrix
from .distances import overlapping_points
from .pbc import minimum_image

def fequal(a, b, tol):
    return (abs(a-b) / max(abs(a), abs(b))) < tol


def moving_average(x, N):
    return np.convolve(x, np.ones((N,))/N)[(N-1):]

def periodic_distance(a, b, periodic):
    '''Periodic distance between two arrays. Periodic is a 3
    dimensional array containing the 3 box sizes.

    '''
    delta = np.abs(a - b)
    delta = np.where(delta > 0.5 * periodic, periodic - delta, delta)
    return np.sqrt((delta ** 2).sum(axis=-1))

def cartesian(arrays, out=None):
    """
    Generate a cartesian product of input arrays.

    Parameters
    ----------
    arrays : list of array-like
        1-D arrays to form the cartesian product of.
    out : ndarray
        Array to place the cartesian product in.

    Returns
    -------
    out : ndarray
        2-D array of shape (M, len(arrays)) containing cartesian products
        formed of input arrays.

    Examples
    --------
    >>> cartesian(([1, 2, 3], [4, 5], [6, 7]))
    array([[1, 4, 6],
           [1, 4, 7],
           [1, 5, 6],
           [1, 5, 7],
           [2, 4, 6],
           [2, 4, 7],
           [2, 5, 6],
           [2, 5, 7],
           [3, 4, 6],
           [3, 4, 7],
           [3, 5, 6],
           [3, 5, 7]])

    """

    arrays = [np.asarray(x) for x in arrays]
    dtype = arrays[0].dtype

    n = np.prod([x.size for x in arrays])
    if out is None:
        out = np.zeros([n, len(arrays)], dtype=dtype)

    m = n / arrays[0].size
    out[:,0] = np.repeat(arrays[0], m)
    if arrays[1:]:
        cartesian(arrays[1:], out=out[0:m,1:])
        for j in xrange(1, arrays[0].size):
            out[j*m:(j+1)*m,1:] = out[0:m,1:]
    return out
    
def geometric_center(r_array):
    '''Return the geometric center given an array of coordinates of
    shape (n_coord, coord_dimensions).

    '''
    
    return np.average(r_array, axis=0)
    
def center_of_mass(r_array, m_array):
    '''Return the mass center given an array of coordinates of shape
    (n_coord, coord_dimensions) and an array of masses (weights).

    '''
    return np.average(r_array, axis=0, weights=m_array)

def dipole_moment(r_array, charge_array):
    '''Return the dipole moment of a neutral system.
    '''
    return np.sum(r_array * charge_array[:, np.newaxis], axis=0)
