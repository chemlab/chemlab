from collections import defaultdict
from functools import partial
from itertools import chain
from random import choice

import numpy as np

from chemlab.utils.pbc import periodic_distance


class CoverTree(object):
    def __init__(self, metric, metric_args=None):
        '''
        CoverTree is an efficient data structure for nearest-neighbor searches on
        an arbitrary metric.
        
        metric could be:
        
        - a callable that takes two arguments f(a, b) a distance between the two entities.
        - a string representing a default metric, available metrics are:
           periodic: require extra argument periodic 
           euclidean: not supported at the moment
           
        Example:
        
        >>> tree = CoverTree(metric='periodic', metric_args={'cell_lengths': [10, 10, 10]})
        
        '''
        self.root = None
        self.maxlevel = 0
        self.minlevel = -1
        self.nodes = {}
        self.ids = 0
        self.metric = metric
        self.metric_args = metric_args
        self._metric_func = self._metric_dist()

    def _metric_dist(self):
        if self.metric == 'periodic':
            if not 'cell_lengths' in self.metric_args:
                raise ValueError('periodic metric require cell_lengths arg')
            periodic = self.metric_args['cell_lengths']
            return lambda a, b, periodic=np.array(periodic): periodic_distance(np.array(a), np.array(b), periodic)
        else:
            raise ValueError('metric %s unsupported.' % self.metric)

    def distance(self, a, b):
        return self._metric_func(a, b)

    def find(self, point):
        if self.root == None:
            raise ValueError('CoverTree is empty.')

            # In case covertree is not big enough we need to start from a bigger level
        start = max(
            int(np.ceil(np.log2(self.distance(point, self.root.data)))),
            self.maxlevel)
        # print 'MAXLEVEL = ', self.maxlevel, 'start =', start
        return self._find(point, [self.root], start)

    def _find(self, point, cover_set, level):
        children = sum([n.getChildren(level - 1) for n in cover_set], [])
        children_dist = [self.distance(point, p.data) for p in children]

        for p in children:
            for q in children:
                if p != q:
                    assert 2 ** (level - 1) <= self.distance(p.data, q.data)

        if level == self.minlevel:
            res = min((p for p in children),
                      key=lambda x: self.distance(point, x.data))
            dist = self.distance(point, res.data)
            return res, dist
        else:
            # print 'available nodes at level', level - 1, ':', children_dist
            # print 'picking', min(children_dist) + 2.0 ** level
            candidates = [c for c in children if self.distance(point, c.data)
                          <= min(children_dist) + 2.0 ** level]

            return self._find(point, candidates, level - 1)

    def insert(self, point):
        # print 'inserting', point, 'root', self.root
        if self.root is None:
            # The first time the function is called we set the root
            self.root = Node(point, index=self._newidx())
            return self.root
        elif self.distance(self.root.data, point) > 2 ** self.maxlevel:
            # In this case, the root is too low, we need to bring up the maxlevel
            root_dist = self.distance(self.root.data, point)
            self.maxlevel = int(np.ceil(np.log2(root_dist)))
            node = Node(point, index=self._newidx())
            self.root.addChild(node, self.maxlevel - 1)
            # print 'inserted', node, 'level', self.maxlevel - 1, 'distance', root_dist
        else:
            return self._insert(point, [self.root], self.maxlevel)

    def insert_many(self, points):
        [self.insert(p) for p in points]

    def _insert(self, point, cover_set, level):
        cover_set = np.array(cover_set)
        separation = 2 ** level

        children = np.array(sum((n.getChildren(level - 1) for n in cover_set),
                                []))
        children_dist = np.array([self.distance(point, c.data) for c in
                                  children])
        children_dist_min = min(children_dist)

        parent_dist = np.array([self.distance(point, p.data) for p in cover_set
                                ])
        parent_dist_min = min(parent_dist)

        # Point must not be present already
        if children_dist_min == 0.0:
            raise ValueError('Point {} is already present.'.format(point))

        elif children_dist_min > separation:
            return False  # No parent found at this level

        else:
            candidates = children[children_dist <= separation]

            found = self._insert(point, candidates, level - 1)
            if found == False and parent_dist_min <= separation:
                # Pick a new parent at this level
                q = choice(cover_set[parent_dist <= separation])

                node = Node(point, index=self._newidx())
                q.addChild(node, level - 1)

                # Update the minlevel
                self.minlevel = min(self.minlevel, level - 1)
                return True
            else:
                # Reference
                # https://github.com/DNCrane/Cover-Tree/blob/master/Cover_Tree.h#L297
                return found

    def _insert_iter(self, point):
        level = self.maxlevel
        cover_set = [self.root]

        while level > self.minlevel:
            # Get children one level below
            children = sum([n.getChildren(level - 1) for n in cover_set], [])
            dist_from_children = self.distance(point, [c.data
                                                       for c in children])
            min_distance_children = min(dist_from_children)

            if min_distance_children > 2 ** level:
                break
            else:
                dist_from_parent = self.distance(point, [p.data
                                                         for p in cover_set])
                min_distance_parent = min(dist_from_parent)

                if min_distance_parent <= 2 ** level:
                    parent_idx = choice((dist_from_parent <= 2 ** level
                                         ).nonzero()[0])
                    parent = cover_set[parent_idx]
                    node_level = level - 1

                # Construct new cover_set
                cover_set = [c for i, c in enumerate(children)
                             if dist_from_children[i] <= 2 ** level]
                level -= 1

        # At the end we add the thing
        # print 'inserted', point, 'parent', parent, 'level', level, 'distance', self.distance(point, parent.data)
        parent.addChild(Node(point, self._newidx()), node_level)
        return

    def _newidx(self):
        self.ids += 1
        return self.ids - 1

    def query_ball(self, point, r):
        if self.root == None:
            return [], []
        level = self.maxlevel
        candidates = [self.root]

        result = set()
        while level > self.minlevel:
            cover_set = sum([c.getChildren(level - 1) for c in candidates], [])

            candidates = []
            for c in cover_set:
                if self.distance(point, c.data) <= r + 2 ** level:
                    candidates.append(c)

            for c in candidates:
                if self.distance(point, c.data) < r:
                    result.add(c)

            level -= 1
        result = list(result)
        return np.array([r.index for r in result]), np.array([self.distance(r.data, point)
                                           for r in result])
    def query_ball_many(self, points, radii):
        if len(points) == 0:
            return np.array([]), np.array([])
        
        return zip(*[self.query_ball(p, r) for p, r in zip(points, radii)])
    
    def visit(self, node, level, callback):
        callback(node, level)
        if level <= self.minlevel:
            return
        else:
            [self.visit(n, level - 1, callback)
             for n in node.getChildren(level)]

    def __repr__(self):
        ret = ['']

        def cb(node, level):
            ret[0] += str(level).ljust(2) + ' ' * (self.maxlevel - level
                                                   ) + str(node.data) + '\n'

        self.visit(self.root, self.maxlevel - 1, cb)
        return ret[0]


class Node:
    # data is an array of values
    def __init__(self, data=None, index=None):
        self.data = data
        self.children = {}  # dict mapping level and children
        self.parent = None
        self.index = index
    # addChild adds a child to a particular Node and a given level i
    def addChild(self, child, i):
        try:
            # in case i is not in self.children yet
            if (child not in self.children[i]):
                self.children[i].append(child)
        except (KeyError):
            self.children[i] = [child]
        child.parent = self

    # getChildren gets the children of a Node at a particular level
    def getChildren(self, level):
        retLst = [self]
        try:
            retLst.extend(self.children[level])
        except (KeyError):
            pass

        return retLst

    # like getChildren but does not return the parent
    def getOnlyChildren(self, level):
        try:
            return self.children[level]
        except (KeyError):
            pass

        return []

    def removeConnections(self, level):
        if (self.parent != None):
            self.parent.children[level + 1].remove(self)
            self.parent = None

    def __str__(self):
        return str(self.index)

    def __repr__(self):
        return str(self.index)
