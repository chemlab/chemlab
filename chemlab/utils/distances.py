# Utilities for distance searching

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
    method: "simple" | "kdtree" | "cell-lists"
       The method to use. *simple* is a brute-force 
       distance search, *kdtree* uses scipy ``ckdtree`` module
       (periodic not available) and *cell-lists* uses the cell
       linked list method.
    """
    if method=="simple":
        raise NotImplementedError()
    elif method=="kdtree":
        raise NotImplementedError()
    elif method=="cell-lists":
        raise NotImplementedError()
    else:
        raise Exception("Method {} not available.".format(method))

