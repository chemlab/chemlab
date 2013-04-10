'''Test for generic utils

'''
import numpy as np
from chemlab.utils.celllinkedlist import CellLinkedList
from chemlab.libs.ckdtree import cKDTree
from chemlab.utils import distances_within
import time

def test_distances():
    coords = np.array([[ 0.47862783,  0.91050104 , 0.37565696], 
                       [ 0.478536  ,  0.21433066 , 0.05656854], 
                       [ 0.27636328,  0.14721663 , 0.80266125], 
                       [ 0.49174243,  0.45646866 , 0.14006564], 
                       [ 0.80192215,  0.85141589 , 0.92175078], 
                       [ 0.9644853 ,  0.6332241  , 0.2114707 ], 
                       [ 0.19803133,  0.5468024  , 0.88794867], 
                       [ 0.3494425 ,  0.43210967 , 0.94125059], 
                       [ 0.99764426,  0.64943748 , 0.38990311], 
                       [ 0.04809691,  0.20231086 , 0.54656047]])
    
    coords = np.around(coords, 2)
    cutoff = 0.2
    print coords
    # Consistency checks
    print "Simple"
    t = time.time()
    dist_simple = distances_within(coords, coords, cutoff, method="simple")
    print -t + time.time()
    print "Cell-lists"
    t = time.time()
    dist_clist = distances_within(coords, coords, cutoff, method="cell-lists")
    print -t + time.time()
    
    print dist_simple
    print dist_clist
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

