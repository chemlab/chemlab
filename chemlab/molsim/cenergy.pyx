# cython: profile=True
import cython
import numpy as np

from libc.math cimport fabs, rint, pow
from chemlab.data import lj
from cython.parallel import prange

cimport numpy as np


ctypedef np.double_t DTYPE_t

@cython.boundscheck(False)
@cython.cdivision(True)
def lennard_jones(np.ndarray[DTYPE_t, ndim=2] coords, type, periodic=False):
    '''Compute Lennard-Jones energy between atoms at position *coords*
    and of type *type*. Return an array of *forces* acting on each
    atom. If periodic is a number, it represents the dimension of the
    box that is centered at 0

    '''
    cdef int i, j
    
    
    cdef double eps, sigma
    cdef double fac, rsq
    
    eps, sigma = lj.typetolj[type]
    
    cdef int n = len(coords)
    cdef np.ndarray[DTYPE_t, ndim=1] d = np.zeros(3)
    cdef double total_energy = 0.0

    cdef int do_periodic
    cdef float boxsize
    
    if periodic is not False:
        do_periodic = 1
        boxsize = periodic
    else:
        do_periodic = 0

    # All cythonized
    for i in range(n):
        for j in range(i+1, n):
            d[0] = coords[j,0] - coords[i,0]
            d[1] = coords[j,1] - coords[i,1]
            d[2] = coords[j,2] - coords[i,2]
            
            if do_periodic:
                d[0] = d[0] - boxsize * rint(d[0]/boxsize)
                d[1] = d[1] - boxsize * rint(d[1]/boxsize)
                d[2] = d[2] - boxsize * rint(d[2]/boxsize)
            
            rsq = d[0]*d[0] + d[1]*d[1] + d[2]*d[2]
            
            total_energy += 4*eps*((pow(sigma, 12) / pow(rsq, 6)) -
                               (pow(sigma, 6) / pow(rsq, 3)))
    
    return total_energy

