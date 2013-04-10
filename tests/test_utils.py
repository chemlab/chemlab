'''Test for generic utils

'''
import numpy as np
from chemlab.utils.celllinkedlist import CellLinkedList
from chemlab.libs.ckdtree import cKDTree
from chemlab.utils import distances_within
import time

def test_distances():
    coords = np.random.random((10000, 3))
    
    cutoff = 0.02
    #print coords
    # Consistency checks
    print "Simple"
    t = time.time()
    dist_simple = distances_within(coords, coords, cutoff, method="simple")
    print -t + time.time()
    print "Cell-lists"
    t = time.time()
    dist_clist = distances_within(coords, coords, cutoff, method="cell-lists")
    print -t + time.time()
    
    assert np.allclose(sorted(dist_simple), sorted(dist_clist))
    
def test_distances_periodic():
    coords = np.array([[0.0, 0.0, 0.0],
                       [0.0, 0.9, 0.0],
                       [0.0, 0.2, 0.0]])
    coords = np.random.random((10000, 3))
    periodic = np.array([1.0, 1.0, 1.0])
    
    cutoff = 0.02
    
    # Consistency checks
    print "Simple"
    t = time.time()
    dist_simple = distances_within(coords, coords, cutoff, method="simple",
                                   periodic=periodic)
    print -t + time.time()

    print "Cell-lists"
    t = time.time()
    dist_clist = distances_within(coords, coords, cutoff,
                                  method="cell-lists", periodic=periodic)
    print -t + time.time()
    
    #print dist_simple
    #print dist_clist

    assert np.allclose(sorted(dist_simple), sorted(dist_clist))
    
    
def test_cell_list():
    test_points = np.array([[0.1, 0.0, 0.0], [0.9, 0.0, 0.0]])
    #test_points = np.random.random((10, 3)) * 10
    cells = CellLinkedList(test_points,
                           periodic=np.array([[10.0, 0.0, 0.0],
                                              [0.0, 10.0, 0.0],
                                              [0.0, 0.0, 10.0]]),
                           spacing=0.15)
    dr = 0.05
    pairs = cells.query_pairs(dr)
    print len(pairs)

    #ck = cKDTree(test_points)
    #pairs = ck.query_pairs(dr)    
    #print len(pairs)
    
    #print sorted(pairs
    
    # Let's try to visualize that with point and lines'

