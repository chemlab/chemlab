'''Test for generic utils

'''
import numpy as np
from chemlab.utils.celllinkedlist import CellLinkedList
from chemlab.libs.ckdtree import cKDTree
from chemlab.utils import distance_matrix
import time
from nose_parameterized import parameterized

from numpy.random import random as nprandom

@parameterized([
    (nprandom((5, 3)) * 2, nprandom((5, 3)) * 2, 0.5), 
    (nprandom((4,3)) - 0.5, nprandom((4,3)) - 0.5, 0.5) # negative nums
])
def test_distances(coords, coords_b, cutoff):
    # Consistency checks
    print "Simple"
    t = time.time()
    dist_simple = distance_matrix(coords, coords_b, cutoff, method="simple")
    print -t + time.time()
    
    print "Cell-lists"
    t = time.time()
    dist_clist = distance_matrix(coords, coords_b, cutoff, method="cell-lists")
    print -t + time.time()
    
    print dist_simple
    print dist_clist.todense()
    assert np.allclose(dist_simple, dist_clist.todense())
    
def test_distances_periodic():
    coords = np.array([[0.0, 0.0, 0.0],
                       [0.0, 0.9, 0.0],
                       [0.0, 0.2, 0.0]])
    coords = np.random.random((1000, 3))
    periodic = np.array([1.0, 1.0, 1.0])
    
    cutoff = 0.1
    
    # Consistency checks
    print "Simple"
    t = time.time()
    dist_simple = distance_matrix(coords, coords, cutoff, method="simple",
                                   periodic=periodic)
    print -t + time.time()

    print "Cell-lists"
    t = time.time()
    dist_clist = distance_matrix(coords, coords, cutoff,
                                  method="cell-lists", periodic=periodic)
    print -t + time.time()
    
    #print dist_simple
    #print dist_clist

    # errors = (dist_simple != dist_clist.todense()).nonzero()
    # iderr = (errors[0][0, 0], errors[1][0,0])

    # print iderr
    # print coords[iderr[0]], coords[iderr[1]]
    # print dist_simple[iderr]
    # print dist_clist[iderr]
    
    
    assert np.allclose(dist_simple, dist_clist.todense())
    
    
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


