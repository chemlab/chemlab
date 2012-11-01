from ..mathutils import direction, distance
import numpy as np

# Eps in meV
# sigma in nm
lj_params = {
    "Ne" : { "eps"  : 3.0840,
             "sigma": 0.2782}
    
}

def lennard_jones(coords, type, periodic=False):
    '''Compute Lennard-Jones forces between atoms at position *coords*
    and of type *type*. Return an array of *forces* acting on each
    atom. If periodic is a number, it represents the dimension of the
    box

    '''
    eps = lj_params[type]["eps"]
    sigma = lj_params[type]["sigma"] 
    
    n = len(coords)
    forces = np.zeros_like(coords)
    # Inefficient, no fancy indexing
    for i in xrange(n):
        for j in xrange(i+1, n):
            d = coords[j] - coords[i]
            if periodic:
                comp_far = np.absolute(d) > periodic*0.5 
                d[comp_far] -= np.sign(d[comp_far]) * periodic
                
            r = np.linalg.norm(d)
            forces[i] += -24*d*eps*(2*(sigma**12 / r**14) - (sigma**6 / r**8))
            forces[j] -= forces[i]
    
    return forces
