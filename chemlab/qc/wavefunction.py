'''Calculate molecular orbitals module'''
import numpy as np

def molecular_orbital(coords, mocoeffs, gbasis):
    '''Return a molecular orbital given the nuclei coordinates, as well as
       molecular orbital coefficients and basis set specification as given by the cclib library.

       The molecular orbital is represented as a function that takes x, y, z coordinates (in a vectorized fashion)
       and returns a real number.

    '''
    
    # Making a closure
    def f(x, y, z, coords=coords, mocoeffs=mocoeffs, gbasis=gbasis):
        # The other functions take nanometers
        return sum(c * bf(x * 10, y*10, z*10) for c, bf in zip(mocoeffs, getbfs(coords * 10, gbasis)))

    return f

from .cgbf import cgbf
def getbfs(coords, gbasis):
    """Convenience function for both wavefunction and density based on PyQuante Ints.py."""

    sym2powerlist = {
        'S' : [(0,0,0)],
        'P' : [(1,0,0),(0,1,0),(0,0,1)],
        'D' : [(2,0,0),(0,2,0),(0,0,2),(1,1,0),(0,1,1),(1,0,1)],
        'F' : [(3,0,0),(2,1,0),(2,0,1),(1,2,0),(1,1,1),(1,0,2),
               (0,3,0),(0,2,1),(0,1,2), (0,0,3)]
        }

    bfs = []
    for i, at_coords in enumerate(coords):
        bs = gbasis[i]
        for sym,prims in bs:
            for power in sym2powerlist[sym]:
                bf = cgbf(at_coords,power)
                for expnt,coef in prims:
                    bf.add_pgbf(expnt,coef)
                bf.normalize()
                bfs.append(bf)

    return bfs