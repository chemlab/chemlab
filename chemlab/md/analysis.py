'''Analysis for statistical ensembles'''
import numpy as np
import time
from scipy.spatial import distance
from chemlab.utils.celllinkedlist import CellLinkedList
from chemlab.utils import distances_within

def rdf(coords_a, coords_b, binsize=0.002,
        cutoff=1.5, periodic=None, normalize=True):
    """Calculate the radial distribution function of *coords_a* against
    *coords_b*.

    **Parameters**
    - coords_a: np.ndarray((3, NA))
        first set of coordinates
    - coords_b: np.ndarray((3, NB))
        coordinates to calculate the RDF against
    - periodic: np.ndarray((3, 3)) or None
        Wether or not include periodic images in the calculation
    - normalize: True or False
        gromacs-like normalization
    - cutoff: 
        where to cutoff the RDF
    
    """
    
    period = periodic[0, 0], periodic[1,1], periodic[2,2]
    distances = distances_within(coords_a, coords_b, cutoff,
                                 np.array(period, dtype=np.double))
    
    n_a = len(coords_a)
    n_b = len(coords_b)

    volume = periodic[0, 0] * periodic[1, 1] * periodic[2, 2]

    int_distances = np.rint(distances/binsize).astype(int)
    hist = np.bincount(int_distances)
    
    bin_edges = np.arange(len(hist)+1) * binsize
        
    
    if normalize:
        dr  = binsize
        normfac = volume/(n_a*n_b)

        # Normalize this by a sphere shell
        for i, r in enumerate(bin_edges[1:]):
            hist[i] /= ((4.0/3.0 * np.pi * (r + 0.5*dr)**3)
                        - (4.0/3.0 * np.pi * (r- 0.5*dr)**3))

        # Normalize by density
        hist = hist * normfac

    # Cutting up to rmax value
        
    width = cutoff/binsize + 1
    return bin_edges[0:width], hist[0:width]

def running_coordination_number(coordinates_a, coordinates_b, periodic, 
                                binsize=0.002, cutoff=1.5):
    """This is the cumulative radial distribution 
    function, also called running coordination number"""
    x, y = rdf(coordinates_a,
               coordinates_b,
               periodic=periodic,
               normalize=False,
               binsize=binsize,
               cutoff=cutoff)
    y = y.astype('float32') / len(coordinates_a)
    y = np.cumsum(y)
    return x, y

def rdf_multi(frames_a, frames_b, sel_a, sel_b,
              periodic, binsize=0.002):

    # I can take unnormalized stuff and normalize at the end
    nframes = len(frames_a)
    rmax = (periodic[0][0,0]/2.0) * 0.99
    nbins = int(rmax / binsize)
    hist = np.zeros(nbins + 1)
    
    volume = 0.0
    for i in range(nframes):
        bins, hist_f = rdf(frames_a[i][sel_a], frames_b[i][sel_b],
                           periodic=periodic[i], cutoff=rmax,
                           normalize=False, binsize=binsize)
        p = periodic[i]
        volume += p[0,0] * p[1,1] * p[2,2]
        
        hist += hist_f
        
    volume /= nframes
    hist /= nframes

    # Normalize everything
    n_a = len(sel_a.nonzero()[0])
    n_b = len(sel_b.nonzero()[0])
    dr  = binsize
    
    bin_edges = np.arange(nbins + 1) * binsize
    normfac = volume/(n_a*n_b)

    # Normalize this by a sphere shell
    for i, r in enumerate(bin_edges[1:]):
        hist[i] /= ((4.0/3.0 * np.pi * (r + 0.5*dr)**3)
                    - (4.0/3.0 * np.pi * (r- 0.5*dr)**3))

    # Normalize by density
    hist = hist * normfac
    
    return bin_edges, hist
