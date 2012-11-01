'''Analysis for statistical ensembles'''
import numpy as np
from ..mathutils import distance

def pair_correlation(system, bins=1000):
    #density = float(system.n)/system.volume
    distances = []
    
    for i in xrange(system.n):
        for j in xrange(i+1, system.n):
            distances.append(distance(system.rarray[i],
                                      system.rarray[j]))
    
    hist, bin_edges = np.histogram(np.array(distances), bins)
    # Normalize this by radial distribution
    dr = bin_edges[1]- bin_edges[0]
    normal_fac = []
    for edge in bin_edges[:-1]:
        normal_fac.append(4*np.pi*edge**2*dr)
    
    return bin_edges[1:], hist/np.array(normal_fac)
