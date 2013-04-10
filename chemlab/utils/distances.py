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
    if method=="simple":
        if periodic:
            return distance_array(coords_a, coords_b, cutoff, periodic.astype(np.double))
        else:
            dist = squareform(cdist(coords_a, coords_b))
            print cdist(coords_a, coords_b)
            return dist[dist < cutoff]
            
    elif method=="cell-lists":
        a = CellLinkedList(coords_a, cutoff, periodic)
        b = CellLinkedList(coords_b, cutoff, periodic)
        dist = a.query_distances_other(b, cutoff)
        return dist
            
            
    else:
        raise Exception("Method {} not available.".format(method))

