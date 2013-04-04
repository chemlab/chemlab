'''Test for generic utils

'''
import numpy as np
from chemlab.utils import CellLinkedList
from chemlab.libs.ckdtree import cKDTree


def test_cell_list():
    test_points = np.array([[0.1, 0.0, 0.0], [0.9, 0.0, 0.0]])
    cells = CellLinkedList(test_points,
                           periodic=np.array([[2.0, 0.0, 0.0],
                                              [0.0, 2.0, 0.0],
                                              [0.0, 0.0, 2.0]]),
                           spacing=0.2)
    dr = 0.2
    pairs = cells.query_pairs(dr)
    print sorted(pairs)
    
    ck = cKDTree(test_points)
    pairs = ck.query_pairs(dr)
    print sorted(pairs)
    
    # Let's try to visualize that with point and lines'

