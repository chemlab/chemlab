'''Calculate molecular orbitals module'''


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
