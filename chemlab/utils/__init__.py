import numpy as np

from .distances import distances_within
from .distances import distance_matrix
from .distances import overlapping_points


def fequal(a, b, tol):
    return (abs(a-b) / max(abs(a), abs(b))) < tol

def minimum_image(coords, pbc):
    """
    Wraps a vector collection of atom positions into the central periodic
    image or primary simulation cell.
    
    Parameters
    ----------
    pos : :class:`numpy.ndarray`, (Nx3)
    Vector collection of atom positions.
    
    Returns
    -------
    wrap : :class:`numpy.ndarray`, (Nx3)
    Returns atomic positions wrapped into the primary simulation
    cell, or periodic image.
    
    """
    wrap = coords + (coords < 0.0)*pbc - (coords > pbc)*pbc
    return wrap

def moving_average(x, N):
    return np.convolve(x, np.ones((N,))/N)[(N-1):]

def periodic_distance(a, b, periodic):
    delta = np.abs(a - b)
    delta = np.where(delta > 0.5 * periodic, periodic - delta, delta)
    return np.sqrt((delta ** 2).sum(axis=-1))
