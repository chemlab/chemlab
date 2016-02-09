from __future__ import print_function
import random

import numpy as np
from nose.tools import assert_raises, eq_, ok_

from chemlab.utils.covertree import CoverTree
from chemlab.utils._covertree import cCoverTree
from chemlab.utils.pbc import periodic_distance

# Reproducibility
random.seed(42)
np.random.seed(42)
np.set_printoptions(precision=2)


def check_invariant(tree):
    level = tree.maxlevel
    parent = [tree.root]

    while level > tree.minlevel:
        ok = True
        for p in parent:
            #print [(p, c, tree.distance(p.data,c.data)) for c in  p.getOnlyChildren(level - 1)]
            ok_(all([tree.distance(p.data, c.data) <= 2 ** level for c in
                     p.getChildren(level - 1)]))

        children = sum([d.getChildren(level - 1) for d in parent], [])

        # Each children is distant from other children at least
        [[ok_(tree.distance(p.data, q.data) >= 2 ** (level - 1))
          for p in children if p != q] for q in children]

        ok_(ok, 'invariant at level %s' % level)
        parent = children
        level = level - 1


def test_insert():
    K = 100

    positions = np.random.uniform(0, 5, (K, 3))
    tree = cCoverTree(metric='periodic',
                      metric_args={'cell_lengths': [10, 10, 10]})

    # Insert single value
    tree.insert(positions[0])
    check_invariant(tree)
    assert_raises(ValueError, tree.insert, positions[0])

    # Insert multiple values
    for p in positions[1:]:
        tree.insert(p)
        check_invariant(tree)

def test_insert_c():
    K = 100

    positions = np.random.uniform(0, 5, (K, 3))
    tree = cCoverTree(metric='periodic',
                     metric_args={'cell_lengths': [10, 10, 10]})

    # Insert single value
    for p in positions[1:]:
        tree.insert(p)
    
    check_invariant(tree)
    
# def test_speed():
#     tree = CoverTree(metric='periodic',
#                      metric_args={'cell_lengths': [10, 10, 10]})
#     positions = np.random.uniform(0, 10, (10000, 3))
#     for p in positions:
#         tree.insert(p)
# 
# def test_speed_c():
#     tree = cCoverTree(metric='periodic',
#                       metric_args={'cell_lengths': [10, 10, 10]})
#     positions = np.random.uniform(0, 10, (10000, 3))
#     for p in positions:
#         tree.insert(p)
#     
#     positions = np.random.uniform(0, 10, (10000, 3))
#     for p in positions:
#         tree.query_ball(p, 0.5)
    
    


# def test_find():
#     K = 100
#     tree = CoverTree(metric='periodic',
#                      metric_args={'cell_lengths': [10, 10, 10]})
#     positions = np.random.uniform(0, 10, (K, 3))
#     tree.insert_many(positions)
#     check_invariant(tree)
# 
#     i = 0
#     for p in np.random.uniform(0, 10, (K * 10, 3)):
#         ct, dist = tree.find(p)
#         bf = periodic_distance(p, positions, np.array([10, 10, 10])).min()
#         dr = dist - bf
#         if dr >= 1e-10:
#             real = np.argmin(periodic_distance(p, positions, np.array([10, 10, 10])))
#             print('CoverTree', dist, ct, 'BruteForce', bf, positions[real], real)
# 
#         assert dr <= 1e-10

# 
# def test_query_ball():
#     tree = CoverTree(metric='periodic',
#                      metric_args={'cell_lengths': [10, 10, 10]})
#     np.random.seed(42)
#     random.seed(42)
#     positions = np.random.uniform(0, 5, (5000, 3))
#     np.set_printoptions(precision=2)
#     for p in positions:
#         node = tree.insert(p)
# 
#     ref = (periodic_distance([1.0, 1.0, 1.0], positions,
#                              np.array([10, 10, 10])) < 3.0).nonzero()[0]
#     res, dist = tree.query_ball([1, 1, 1], 3.0)
#     eq_(len(ref), len(res))
