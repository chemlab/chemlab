# Utilities for distance searching
import numpy as np
from scipy.spatial.distance import cdist, squareform

from ..libs.ckdtree import cKDTree
from .cdist import distance_array
from .celllinkedlist import CellLinkedList

def distances_within(coords_a, coords_b, cutoff,
                     periodic=False, method="simple"):
    """Calculate distances between the array of coordinates *coord_a*
    and *coord_b* within a certain cutoff.
    
    This function is a wrapper around different routines and data structures
    for distance searches. It return a np.ndarray containing the distances.
    
    **Parameters**

    coords_a: np.ndarray((N, 3), dtype=float)
       First coordinate array
    coords_b: np.ndarray((N, 3), dtype=float)
       Second coordinate array
    cutoff: float
       Maximum distance to search for
    periodic: False or np.ndarray((3,), dtype=float)
       If False, don't consider periodic images. Otherwise
       periodic is an array containing the periodicity in the
       3 dimensions.
    method: "simple" | "cell-lists"
       The method to use. *simple* is a brute-force 
       distance search, *kdtree* uses scipy ``ckdtree`` module
       (periodic not available) and *cell-lists* uses the cell
       linked list method.
    """
    mat = distance_matrix(coords_a, coords_b, cutoff, periodic, method)
    return mat[mat.nonzero()]

def distance_matrix(coords_a, coords_b, cutoff,
                    periodic=False, method="simple"):
    """Calculate distances matrix the array of coordinates *coord_a*
    and *coord_b* within a certain cutoff.
    
    This function is a wrapper around different routines and data structures
    for distance searches. It return a np.ndarray containing the distances.
    
    Returns a matrix with all the computed distances. When using the
    "cell-lists" method it returns a scipy.sparse.dok_matrix.
    
    **Parameters**

    coords_a: np.ndarray((N, 3), dtype=float)
       First coordinate array
    coords_b: np.ndarray((N, 3), dtype=float)
       Second coordinate array
    cutoff: float
       Maximum distance to search for
    periodic: False or np.ndarray((3,), dtype=float)
       If False, don't consider periodic images. Otherwise
       periodic is an array containing the periodicity in the
       3 dimensions.
    method: "simple" | "cell-lists"
       The method to use. *simple* is a brute-force 
       distance search, and *cell-lists* uses the cell
       linked list method.

    """
    coords_a = np.array(coords_a)
    coords_b = np.array(coords_b)
    if method=="simple":
        if periodic is not False:
            return distance_array(coords_a, coords_b, cutoff=cutoff,
                                  period=periodic.astype(np.double))
        else:
            dist = cdist(coords_a, coords_b)
            dist[dist > cutoff] = 0
            return dist
            
    elif method=="cell-lists":
        if periodic is not False:
            if np.any(cutoff > periodic/2):
                raise Exception("Not working with such a big cutoff.")
            
        # We need all positive elements
        mina = coords_a[:, 0].min(), coords_a[:, 1].min(), coords_a[:, 2].min()
        minb = coords_b[:, 0].min(), coords_b[:, 1].min(), coords_b[:, 2].min()
        # Find the lowest        
        origin = np.minimum(mina, minb)
        
        a = CellLinkedList(coords_a - origin, cutoff, periodic)
        b = CellLinkedList(coords_b - origin, cutoff, periodic)
        dist = a.query_distances_other(b, cutoff)
        return dist
            
            
    else:
        raise Exception("Method {} not available.".format(method))

def overlapping_points(coords_a, coords_b, cutoff, periodic=False):
    '''Return the indices of *coords_b* points that overlap with
    *coords_a* points. The overlap is calculated based on *cutoff*.

    **Parameters**
    
    coords_a: np.ndarray((NA, 3))
    
    coords_b: np.ndarray((NB, 3))
    
    cutoff: float
       Distance within two points are considered overlapping.
    
    periodic: False or np.ndarray(3)
       Periodicity in x, y, z dimensions
    
    '''
    
    res = distance_matrix(coords_a, coords_b, periodic=periodic, 
                          cutoff=cutoff, method="cell-lists")
    overlaps = res.nonzero()[1]
    return np.unique(overlaps)
