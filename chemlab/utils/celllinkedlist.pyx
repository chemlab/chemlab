from __future__ import division
import numpy as np
cimport numpy as np
cimport cython

cdef extern from "math.h":
    double sqrt(double)

cdef int EMPTY = -1

cdef class CellLinkedList:
    '''Generic cell linked list data structure
    Reference at http://cacs.usc.edu/education/cs596/01-1LinkedListCell.pdf
    
    **Parameters**
    points: np.ndarray((N, 3))
       Array of 3d coordinates. Each coordinate should be > 0.
    periodic: np.ndarray((3, 3)) or None
       Whether or not include periodic images in the 
       calculation
    spacing: float
       Approximate spacing between cells, the spacing will be
       recalculated to divide the space in equal cells.
    
    '''
    cdef readonly np.ndarray points
    cdef readonly np.ndarray periodic
    cdef np.ndarray point_linked_list
    cdef np.ndarray cell_heads
    cdef int n_points
    cdef int n_cells
    cdef int[3] divisions
    
    def __init__(CellLinkedList self, points, periodic, spacing):
        self.points = points
        self.periodic = periodic
        self.n_points = len(points)
        
        # First of all determine the divisions
        
        # For now assume orthogonal box
        a, b, c = periodic[0,0], periodic[1,1], periodic[2,2]

        self.divisions[0] = int(a/spacing)
        self.divisions[1] = int(b/spacing)
        self.divisions[2] = int(c/spacing)
        
        self.n_cells = self.divisions[0]*self.divisions[1]*self.divisions[2]
        
        # True spacing required to make the boxes like squares
        rc = np.array([a/self.divisions[0], b/self.divisions[1], c/self.divisions[2]])
        
        # Build the CellLinkedList
        
        # The i-th elemen hold the atom index linked to the i-th point
        self.point_linked_list = np.zeros(self.n_points, dtype=int)
        self.point_linked_list[:] = EMPTY
        
        # Contain the first atom in a cell
        self.cell_heads = np.zeros((self.divisions[0],
                                    self.divisions[1],
                                    self.divisions[2]), dtype='i4')
        self.cell_heads[:] = EMPTY

        for i in xrange(self.n_points):
            # Cell index to which the atom belongs
            ind = (self.points[i]/rc).astype(int)
            
            ind = (ind + ind.shape)%ind.shape
            # Copy the previous head to the linked_list
            self.point_linked_list[i] = self.cell_heads[tuple(ind)]

            
            # Last goes to head
            self.cell_heads[tuple(ind)] = i

    def query_distances_other(self, CellLinkedList other, double dr):
        # Other must have the same number of cells...
        distances = []
        
        cdef int i, j, k
        cdef int ni, nj, nk
        cdef int da, db, dc
        cdef int i_point, j_point
        cdef double [:] shift = np.zeros(3, dtype=np.float64)
        cdef int [:, :, :] cell_heads = self.cell_heads
        cdef int [:, :, :] other_cell_heads = other.cell_heads
        cdef double [:] rij, ri, rj, 
        cdef double dist
        
        rij = np.zeros(3, dtype=np.float64)
        
        da = self.divisions[0]
        db = self.divisions[1]
        dc = self.divisions[2]

        # We have to iterate over all cells
        for i in xrange(da):
            for j in xrange(db):
                for k in xrange(dc):

                    # Scan over the neighbour cells
                    for ni in xrange(i-1, i+1):
                        for nj in xrange(j-1, j+1):
                            for nk in xrange(k-1, k+1):

                                # Periodic boundary shift
                                if ni < 0:
                                    shift[0] = - self.periodic[0, 0]
                                elif ni >= da:
                                    shift[0] = self.periodic[0, 0]
                                else:
                                    shift[0] = 0
                                    
                                if nj < 0:
                                    shift[1] = - self.periodic[1, 1]
                                elif nj >= db:
                                    shift[1] = self.periodic[1, 1]
                                else:
                                    shift[1] = 0
                                if nk < 0:
                                    shift[2] = - self.periodic[2, 2]
                                elif nk >= dc:
                                    shift[2] = self.periodic[2, 2]
                                else:
                                    shift[2] = 0
                                
                                # Scan atom i in the central cell
                                i_point = cell_heads[i, j, k]

                                while (i_point != EMPTY):
                                    # Scan point in the neighbour cell
                                    j_point = other_cell_heads[(ni+da)%da,
                                                               (nj+db)%db,
                                                               (nk+dc)%dc]
                                    
                                    # This is taken from the other
                                    while (j_point != EMPTY):
                                        # Avoid double counting
                                        if i_point < j_point:
                                            ri = self.points[i_point]
                                            rj = other.points[j_point]
                                          
                                            # Shift by minimum image
                                            for xx in range(3):
                                                rij[xx] = ri[xx] - (rj[xx]+shift[xx])
                                            
                                            dist = rij[0]*rij[0] + rij[1]*rij[1] + rij[2]*rij[2]
                                          
                                            if (dist < dr**2):
                                                distances.append(sqrt(dist))
                                            
                                        j_point = other.point_linked_list[j_point]
                                    i_point = self.point_linked_list[i_point]
        
        return distances
        
    @cython.boundscheck(False)        
    def query_pairs(self, double dr):
        # To query pairs we have to do a little bit of struggling
        pairs = []
        
        cdef int i, j, k
        cdef int ni, nj, nk
        cdef int da, db, dc
        cdef int i_point, j_point
        cdef double [:] shift = np.zeros(3, dtype=np.float64)
        cdef int [:, :, :] cell_heads = self.cell_heads
        cdef double [:] rij, ri, rj, 
        cdef double dist
        
        rij = np.zeros(3, dtype=np.float64)
        
        da = self.divisions[0]
        db = self.divisions[1]
        dc = self.divisions[2]

        # We have to iterate over all cells
        for i in xrange(da):
            for j in xrange(db):
                for k in xrange(dc):

                    # Scan over the neighbour cells
                    for ni in xrange(i-1, i+1):
                        for nj in xrange(j-1, j+1):
                            for nk in xrange(k-1, k+1):

                                # Periodic boundary shift
                                if ni < 0:
                                    shift[0] = - self.periodic[0, 0]
                                elif ni > da:
                                    shift[0] = self.periodic[0, 0]
                                else:
                                    shift[0] = 0
                                    
                                if nj < 0:
                                    shift[1] = - self.periodic[1, 1]
                                elif nj > db:
                                    shift[1] = self.periodic[1, 1]
                                else:
                                    shift[1] = 0
                                if nk < 0:
                                    shift[2] = - self.periodic[2, 2]
                                elif nk > dc:
                                    shift[2] = self.periodic[2, 2]
                                else:
                                    shift[2] = 0
                                
                                # Scan atom i in the central cell
                                i_point = cell_heads[i, j, k]

                                while (i_point != EMPTY):
                                    # Scan point in the neighbour cell
                                    j_point = cell_heads[(ni+da)%da,
                                                         (nj+db)%db,
                                                         (nk+dc)%dc]
                                    while (j_point != EMPTY):
                                        # Avoid double counting
                                        if i_point < j_point:
                                            ri = self.points[i_point]
                                            rj = self.points[j_point]
                                            # Shift by minimum image
                                            
                                            for xx in range(3):
                                                rij[xx] = ri[xx] - (rj[xx]+shift[xx])
                                            
                                            dist = rij[0]*rij[0] + rij[1]*rij[1] + rij[2]*rij[2]
                                            
                                            if (dist < dr**2):
                                                pairs.append((i_point, j_point))

                                            
                                        j_point = self.point_linked_list[j_point]
                                    i_point = self.point_linked_list[i_point]
        
        return pairs

        
def minimum_image_distance(a, b, periodic):
    d = b - a
    d[0] = d[0] - periodic[0] * int(d[0]/periodic[0])
    d[1] = d[1] - periodic[1] * int(d[1]/periodic[1])
    d[2] = d[2] - periodic[2] * int(d[2]/periodic[2])
    
    return np.sqrt((d*d).sum())
