'''Analysis for statistical ensembles'''
import numpy as np
import time
from scipy.spatial import distance
from chemlab.utils.celllinkedlist import CellLinkedList
from chemlab.utils import distances_within

def radial_distribution_function(coords_a, coords_b, nbins=1000, cutoff=1.5, periodic=None, normalize=True):
    """Calculate the radial distribution function of *coords_a* against
    *coords_b*.

    **Parameters**
    - coords_a: np.ndarray((3, NA))
        first set of coordinates
    - coords_b: np.ndarray((3, NB))
        coordinates to calculate the RDF against
    - periodic: np.ndarray((3, 3)) or None
        Wether or not include periodic images in the calculation
    - normalize: True or False
        gromacs-like normalization
    - cutoff: 
        where to cutoff the RDF
    
    """
    
    # Make the linked list
    # cl = CellLinkedList(coords_a,
    #                     periodic=periodic,
    #                     spacing = cutoff)
    
    # cl2 = CellLinkedList(coords_b,
    #                     periodic=periodic,
    #                     spacing = cutoff)

    # distances = cl.query_distances_other(cl2, cutoff)

    period = periodic[0, 0], periodic[1,1], periodic[2,2]
    distances = distances_within(coords_a, coords_b, cutoff,
                                 np.array(period, dtype=np.double))
    n_a = len(coords_a)
    n_b = len(distances)/float(n_a)

    rmin = 0.0
    bins = np.linspace(rmin, cutoff, nbins)
    vmax = (4.0/3.0) * np.pi * cutoff ** 3
    local_rho = n_b / vmax

    hist, bin_edges = np.histogram(distances, bins)
    dr  = bin_edges[1] - bin_edges[0]
    
    # Normalize this by a sphere shell
    for i, r in enumerate(bin_edges[1:]):
        hist[i] /= ((4.0/3.0 * np.pi * (r+dr)**3) - (4.0/3.0 * np.pi * (r)**3))
        
    
    if normalize:
         hist = hist/(local_rho*n_a)
    
    return bin_edges[:-1], hist

