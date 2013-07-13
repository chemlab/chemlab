# distutils: language = c++
'''Speedup distance computations

'''
import numpy as np
cimport numpy as np
cimport cython
from scipy.sparse import dok_matrix

from libc.math cimport sqrt, floor

@cython.boundscheck(False)
def distance_array(arr_a, arr_b, double[:] period, double cutoff):
    cdef int i, j
    cdef int na = len(arr_a), nb = len(arr_b)
    cdef int size
    cdef double dist
    
    cdef double[:] distbuf
    
    cdef double[:,:] bufa = arr_a.astype(np.double)
    cdef double[:,:] bufb = arr_b.astype(np.double)
    
    distmat = np.zeros((na, nb), np.double)
    cdef double[:,:] d_mat = distmat
    
    for i in range(na):
        for j in range(nb):
            dist = minimum_image_distance(bufa[i], bufb[j], period)
            if dist <= cutoff:
                d_mat[i,j] = dist
    
    return distmat
        

@cython.cdivision(True)
@cython.boundscheck(False)
cdef inline double minimum_image_distance(double[:] a,double[:] b, double[:] periodic) nogil:
    cdef double d[3]
    cdef double a_can, b_can 
    
    for i in range(3):
        a_can = a[i] - floor(a[i]/periodic[i]) * periodic[i]
        b_can = b[i] - floor(b[i]/periodic[i]) * periodic[i]
        
        d[i] = b_can - a_can
        d[i] = d[i] - periodic[i] * rint(d[i]/periodic[i])
    
    return sqrt(d[0]*d[0] + d[1]*d[1] + d[2]*d[2])
