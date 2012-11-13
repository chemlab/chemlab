# cython: profile=True
import cython
import numpy as np

from libc.math cimport fabs, rint, pow, abs, copysign
from chemlab.data import lj
from cython.parallel import prange

cimport numpy as np
ctypedef np.double_t DTYPE_t

cdef extern from "cmpforces.h":
    void omplennard_jones(double *coords, double *out, int dim, double sigma, double eps, int periodic, double boxsize) nogil

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
    cdef np.ndarray[DTYPE_t, ndim=1] d = np.zeros(3)
    cdef int do_periodic = 1
    cdef double boxsize = 0.0
    
    if periodic:
        do_periodic = 1
        boxsize = float(periodic)
    else:
        do_periodic = 0

    
    with nogil:
        omplennard_jones(<double *> coords.data,<double *> forces.data, n, sigma, eps, do_periodic, boxsize)
    
    return forces
