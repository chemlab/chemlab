from __future__ import division
import numpy as np

EMPTY = -1

class CellLinkedList(object):
    def __init__(self, points, periodic, spacing):
        self.points = points
        self.periodic = periodic
        self.n_points = len(points)
        
        # First of all determine the divisions
        
        # For now assume orthogonal box
        a, b, c = periodic[0,0], periodic[1,1], periodic[2,2]
        DIVISIONS_A = int(a/spacing)
        DIVISIONS_B = int(b/spacing)
        DIVISIONS_C = int(c/spacing)

        self.n_cells = DIVISIONS_A*DIVISIONS_B*DIVISIONS_C
        
        # True spacing required to make the boxes like squares
        rc = np.array([a/DIVISIONS_A, b/DIVISIONS_B, c/DIVISIONS_C])
        
        # Build the CellLinkedList
        
        # The i-th elemen hold the atom index linked to the i-th point
        self.point_linked_list = np.zeros(self.n_points, dtype=int)
        self.point_linked_list[:] = EMPTY
        
        # Contain the first atom in a cell
        self.cell_heads = np.zeros((DIVISIONS_A,
                                    DIVISIONS_B,
                                    DIVISIONS_C), dtype=int)
        self.cell_heads[:] = EMPTY

        for i in xrange(self.n_points):
            # Cell index to which the atom belongs
            ind = (self.points[i]/rc).astype(int)
            
            # Copy the previous head to the linked_list
            self.point_linked_list[i] = self.cell_heads[tuple(ind)]

            
            # Last goes to head
            self.cell_heads[tuple(ind)] = i
        
    def query_pairs(self, dr):
        # To query pairs we have to do a little bit of struggling
        pairs = []
        
        da, db, dc = self.cell_heads.shape
        # We have to iterate over all cells
        for i in range(da):
            for j in range(db):
                for k in range(dc):

                    # Scan over the neighbour cells
                    for ni in (i-1, i, i+1):
                        for nj in (j-1, j, j+1):
                            for nk in (k-1, k, k+1):
                                shift = np.zeros(3)
                                # Periodic boundary shift
                                if ni < 0:
                                    shift[0] = - self.periodic[0, 0]
                                elif ni > da:
                                    shift[0] = self.periodic[0, 0]
                                if nj < 0:
                                    shift[1] = - self.periodic[1, 1]
                                elif nj > db:
                                    shift[1] = self.periodic[1, 1]
                                if nk < 0:
                                    shift[2] = - self.periodic[2, 2]
                                elif nk > dc:
                                    shift[2] = self.periodic[2, 2]
                                
                                # Scan atom i in the central cell
                                i_point = self.cell_heads[i, j, k]
                                while (i_point != EMPTY):
                                    # Scan point in the neighbour cell
                                    j_point = self.cell_heads[(ni+da)%da,
                                                              (nj+db)%db,
                                                              (nk+dc)%dc]
                                    while(j_point != EMPTY):
                                        # Avoid double counting
                                        if i_point < j_point:
                                            ri = self.points[i_point]
                                            rj = self.points[j_point]
                                            # Shift by minimum image
                                            rij = ri - (rj+shift)
                                            
                                            if (rij*rij).sum() < dr**2:
                                                pairs.append((i_point, j_point))
                                        j_point = self.point_linked_list[j_point]
                                    i_point = self.point_linked_list[i_point]
        
        return pairs