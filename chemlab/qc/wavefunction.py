'''Calculate molecular orbitals module'''
import numpy as np

def molecular_orbital(coords, mocoeffs, gbasis):
    
    # Making a closure
    def f(x, y, z, coords=coords, mocoeffs=mocoeffs, gbasis=gbasis):
        return sum(c * bf(x, y, z) for c, bf in zip(mocoeffs, getbfs(coords, gbasis)))

    return f

def wavefunction(coords, mocoeffs, gbasis, volume):
    """Calculate the magnitude of the wavefunction at every point in a volume.
    
    Attributes:
        coords -- the coordinates of the atoms
        mocoeffs -- mocoeffs for one eigenvalue
        gbasis -- gbasis from a parser object
        volume -- a template Volume object (will not be altered)
    """
    bfs = getbfs(coords, gbasis)
    
    wavefn = copy.copy(volume)
    wavefn.data = numpy.zeros( wavefn.data.shape, "d")

    conversion = convertor(1,"bohr","Angstrom")
    x = numpy.arange(wavefn.origin[0], wavefn.topcorner[0]+wavefn.spacing[0], wavefn.spacing[0]) / conversion
    y = numpy.arange(wavefn.origin[1], wavefn.topcorner[1]+wavefn.spacing[1], wavefn.spacing[1]) / conversion
    z = numpy.arange(wavefn.origin[2], wavefn.topcorner[2]+wavefn.spacing[2], wavefn.spacing[2]) / conversion

    for bs in range(len(bfs)):
        data = numpy.zeros( wavefn.data.shape, "d")
        for i,xval in enumerate(x):
            for j,yval in enumerate(y):
                for k,zval in enumerate(z):
                    data[i, j, k] = bfs[bs].amp(xval,yval,zval)
        numpy.multiply(data, mocoeffs[bs], data)
        numpy.add(wavefn.data, data, wavefn.data)
    
    return wavefn

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