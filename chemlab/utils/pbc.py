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


def subtract_vectors(vec_a, vec_b, periodic):
    '''Returns the difference of the points vec_a - vec_b subject 
       to the periodic boundary conditions.

    '''
    moved = noperiodic(np.array([vec_b, vec_a]), periodic)
    return vec_a - vec_b


def add_vectors(vec_a, vec_b, periodic):
    '''Returns the sum of the points vec_a - vec_b subject 
       to the periodic boundary conditions.

    '''
    moved = noperiodic(np.array([vec_a, vec_b]), periodic)
    return vec_a + vec_b