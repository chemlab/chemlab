# cython: profile=True
import cython
import numpy as np

from libc.math cimport fabs, rint, pow, abs, copysign
from chemlab.data import lj
from cython.parallel import prange

cimport numpy as np

ctypedef np.float32_t DTYPE_t

@cython.boundscheck(False)
@cython.cdivision(True)
def lennard_jones(np.ndarray[DTYPE_t, ndim=2] coords, type, periodic=False):
    '''Compute Lennard-Jones forces between atoms at position *coords*
    and of type *type*. Return an array of *forces* acting on each
    atom. If periodic is a number, it represents the dimension of the
    box

    '''
    cdef int i, j
    
    cdef double eps, sigma
    eps, sigma = lj.typetolj[type]
    
    cdef double fac, rsq
    cdef int n = len(coords)
    cdef np.ndarray[DTYPE_t, ndim=2] forces = np.zeros_like(coords)
    cdef np.ndarray[DTYPE_t, ndim=1] d = np.zeros(3).astype(np.float32)
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
            
            # let's compute the periodicity            
            if do_periodic:
                # Those are equivalent periodic conditions, just to
                # get rid of some if statements
                d[0] = d[0] - boxsize * rint(d[0]/boxsize)
                d[1] = d[1] - boxsize * rint(d[1]/boxsize)
                d[2] -= d[2] - boxsize * rint(d[2]/boxsize)
                
                # if fabs(d[0]) > boxsize*0.5:
                #     d[0] = d[0] - copysign(boxsize, d[0])
                # if fabs(d[1]) > boxsize*0.5:
                #     d[1] = d[1] - copysign(boxsize, d[1])
                # if fabs(d[2]) > boxsize*0.5:
                #     d[2] = d[2] - copysign(boxsize, d[2])
            
            
            rsq = d[0]*d[0] + d[1]*d[1] + d[2]*d[2]
            s6 = pow(sigma, 6)
            s12 = s6*s6
            fac = -24*eps*(2*(s12/pow(rsq, 7)) -
                          (s6/pow(rsq, 4)))
            

            forces[i,0] += fac*d[0]
            forces[i,1] += fac*d[1]
            forces[i,2] += fac*d[2]
            
            forces[j,0] -= forces[i,0]
            forces[j,1] -= forces[i,1]
            forces[j,2] -= forces[i,2]            
    
    return forces
