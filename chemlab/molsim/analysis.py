'''Analysis for statistical ensembles'''
import numpy as np
import time
from scipy.spatial import distance



def radial_distribution_function(system, maska, maskb, nbins=1000, rmax=1.5):
    distances = distance.cdist(system.r_array[maska], system.r_array[maskb])
    # Filtering distances outside rmax
    distances = distances[distances < rmax]
    
    n_a = len(system.r_array[maska])
    n_b = len(distances)/float(n_a)
    
    rmin = 0.0
    bins = np.linspace(rmin, rmax, nbins)
    vmax = (4.0/3.0) * np.pi * rmax ** 3
    local_rho = n_b / vmax
    
    hist, bin_edges = np.histogram(distances, bins)
    dr  = bin_edges[1] - bin_edges[0]

    # Normalize this by a sphere shell
    for i, r in enumerate(bin_edges[1:]):
        hist[i] /= 4.0 * np.pi * (r+dr)**2
    
    return bin_edges[1:], 1.0/(local_rho*n_a) * hist
