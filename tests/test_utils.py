'''Test for generic utils

'''
import numpy as np
from chemlab.utils import CellLinkedList
from chemlab.libs.ckdtree import cKDTree


def test_cell_list():
    test_points = np.array([[0.1, 0.0, 0.0], [0.9, 0.0, 0.0]])
    test_points = np.random.random((10000, 3)) * 10
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

