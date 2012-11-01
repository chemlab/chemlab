# cython: profile=True
from ..mathutils import direction, distance
import cython
import numpy as np
import math
cimport numpy as np

# Eps in meV
# sigma in nm
lj_params = {
    "Ne" : { "eps"  : 3.0840,
             "sigma": 0.2782}
    
}
ctypedef np.float32_t DTYPE_t

@cython.boundscheck(False)
def lennard_jones(np.ndarray[DTYPE_t, ndim=2] coords, type, periodic=False):
    '''Compute Lennard-Jones forces between atoms at position *coords*
    and of type *type*. Return an array of *forces* acting on each
    atom. If periodic is a number, it represents the dimension of the
    box

    '''
    cdef int i, j
    
    cdef float eps = lj_params[type]["eps"]
    cdef float sigma = lj_params[type]["sigma"] 
    
    cdef int n = len(coords)
    cdef np.ndarray[DTYPE_t, ndim=2] forces = np.zeros_like(coords)
    cdef np.ndarray[DTYPE_t, ndim=1] d = np.zeros(3).astype(np.float32)
    
    # Inefficient, no fancy indexing
    for i in range(n):
        for j in range(i+1, n):
            d[0] = coords[j,0] - coords[i,0]
            d[1] = coords[j,1] - coords[i,1]
            d[2] = coords[j,2] - coords[i,2]
            if periodic:
                comp_far = np.absolute(d) > periodic*0.5 
                d[comp_far] -= np.sign(d[comp_far]) * periodic
                
            rsq = d[0]*d[0] + d[1]*d[1] + d[2]*d[2]
            
            forces[i] += -24*d*eps*(2*(sigma**12 / rsq**7) - (sigma**6 / rsq**4))
            forces[j] -= forces[i]
    
    return forces
