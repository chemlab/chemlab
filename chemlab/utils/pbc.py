import numpy as np


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


def noperiodic(r_array, periodic, reference=None):
    '''Rearrange the array of coordinates *r_array* in a way that doensn't
       cross the periodic boundary.

       Parameters
       ----------
       r_array : :class:`numpy.ndarray`, (Nx3)
       Array of 3D coordinates.
       
       periodic: :class:`numpy.ndarray`, (3)
       Periodic boundary dimensions.

       reference: ``None`` or :class:`numpy.ndarray` (3)
       The points will be moved to be in the periodic image centered on the reference. 
       If None, the first point will be taken as a reference
    
       Returns
       -------

       A (N, 3) array of coordinates, all in the same periodic image.

       Example
       -------

           >>> coordinates = np.array([[0.1, 0.0, 0.0], [0.9, 0.0, 0.0]])
           >>> periodic = np.array([1, 1, 1])
           >>> noperiodic(coordinates, periodic)
           [[ 0.1, 0.0, 0.0],
            [-0.1, 0.0, 0.0]]

    '''
    if reference is None:
        center = r_array[0]
    else:
        center = reference
    
    # Find the displacements
    dr = (center - r_array)
    drsign = np.sign(dr)

    # Move things when the displacement is more than half the box size
    tomove = np.abs(dr) >= periodic/2.0
    r_array[tomove] += (drsign * periodic)[tomove]
    return r_array


def subtract_vectors(a, b, periodic):
    '''Returns the difference of the points vec_a - vec_b subject 
       to the periodic boundary conditions.

    '''
    r = a - b
    delta = np.abs(r)
    sign = np.sign(r)
    return np.where(delta > 0.5 * periodic, sign * (periodic - delta), r)


def add_vectors(vec_a, vec_b, periodic):
    '''Returns the sum of the points vec_a - vec_b subject 
       to the periodic boundary conditions.

    '''
    moved = noperiodic(np.array([vec_a, vec_b]), periodic)
    return vec_a + vec_b


def distance_matrix(coordinates, periodic):
    '''

    '''
    a = coordinates
    b = coordinates[:, np.newaxis]
    return periodic_distance(a, b, periodic)

def periodic_distance(a, b, periodic):
    '''Periodic distance between two arrays. Periodic is a 3
    dimensional array containing the 3 box sizes.

    '''
    delta = np.abs(a - b)
    delta = np.where(delta > 0.5 * periodic, periodic - delta, delta)
    return np.sqrt((delta ** 2).sum(axis=-1))


def geometric_center(coords, periodic):
    '''Geometric center taking into account periodic boundaries'''
    max_vals = periodic
    theta = 2*np.pi*(coords / max_vals)
    eps = np.cos(theta) * max_vals/(2*np.pi)
    zeta = np.sin(theta) * max_vals/(2*np.pi)

    eps_avg = eps.sum(axis=0)
    zeta_avg = zeta.sum(axis=0)
    theta_avg = np.arctan2(-zeta_avg, -eps_avg) + np.pi

    return theta_avg * max_vals /(2*np.pi)


def radius_of_gyration(coords, periodic):
    '''Calculate the square root of the mean distance squared from the center of gravity.

    '''
    gc = geometric_center(coords, periodic)
    return (periodic_distance(coords, gc, periodic)**2).sum()/len(coords)