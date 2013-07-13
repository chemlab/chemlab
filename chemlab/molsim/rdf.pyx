# Cython version of radial distribution function
import numpy as np
cimport numpy as np
cimport cython

from chemlab.utils.cdist cimport minimum_image_distance, rint

@cython.boundscheck(False)
@cython.cdivision(True)
def distance_histogram(arr_a, arr_b, double binsize=0.002, double cutoff=1.5, periodic=None):
    cdef int i, j
    cdef int na = len(arr_a), nb = len(arr_b)
    cdef int size
    cdef double dist
    
    cdef double[:] period = np.array([periodic[0,0], periodic[1,1], periodic[2,2]])
    cdef double[:] distbuf
    
    cdef double[:,:] bufa = arr_a.astype(np.double)
    cdef double[:,:] bufb = arr_b.astype(np.double)
    
    edges = np.arange(0, cutoff, binsize)
    hist = np.zeros_like(edges, 'int')
    cdef long[:] hist_buf = hist
    cdef int place
    cdef int maxhist = len(hist)
    
    for i in range(na):
        for j in range(nb):
            dist = minimum_image_distance(bufa[i], bufb[j], period)
            place = <int> rint(dist/binsize)
            if place < maxhist:
                hist_buf[place] += 1
    
    return hist
