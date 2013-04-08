'''Speed utilities'''

import numpy as np
cimport numpy as np
cimport cython
from cython.view cimport array as cyarray
from ..transformations import (normalized,
                               unit_vector, distance)
from ..transformations import angle_between_vectors as t_angle_between_vectors
from ..transformations import vector_product as t_vector_product
from ..transformations import rotation_matrix as t_rotation_matrix

import time

cdef extern from "math.h":
    double acos(double x)    
    double sqrt(double x)
    double sin(double x)
    double cos(double x)
    double fabs(double x)

cdef double dot(double[:] a, double[:] b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

cdef void vector_product(double[:] a, double[:] b, double[:] out):
    out[0] = a[1]*b[2] - a[2]*b[1]
    out[1] = a[2]*b[0] - a[0]*b[2]
    out[2] = a[0]*b[1] - a[1]*b[0]
    

cdef double norm(double[:] a):
    return sqrt(dot(a, a))

cdef double angle_between_vectors(double[:] a, double[:] b):
    return acos(dot(a,b)/(norm(a) * norm(b)))
    
cdef void vec3_sub(double[:] a, double[:] b, double[:] out):
    cdef int i
    for i in range(3):
        out[i] = a[i] - b[i]


cdef int allclose_d(double[:] a,double[:] b):
    cdef double eps = 1e-9
    cdef int n = len(a)
    cdef int i
    cdef int ret = 1
    
    for i in range(n):
        ret = ret and (fabs(a[i] - b[i]) < eps)
        
    return ret

@cython.boundscheck(False)
cdef void rotation_matrix(double angle, double[:] d, double[:, :] M):
     """
     Create a rotation matrix corresponding to the rotation around a general
     axis by a specified angle.

     R = dd^T + cos(a) (I - dd^T) + sin(a) skew(d)

     Parameters:

         angle : float a
         direction : array d
     """
     cdef double cost = cos(angle)
     cdef double sint = sin(angle)
     cdef double ux, uy, uz
     
     ux = d[0]
     uy = d[1]
     uz = d[2]
     
     M[0, 0] = cost + ux*ux*(1-cost)
     M[1, 0] = ux*uy*(1 - cost) - uz*sint
     M[2, 0] = ux*uz*(1 - cost) + uy*sint
     
     M[0, 1] = uy*ux*(1 - cost) + uz*sint
     M[1, 1] = cost + uy*uy*(1 - cost)
     M[2, 1] = uy*uz*(1-cost) - ux*sint

     M[0, 2] = uz*ux*(1-cost) - uy*sint
     M[1, 2] = uz*uy*(1-cost) + ux*sint
     M[2, 2] = cost + uz*uz*(1-cost)
     
     

@cython.boundscheck(False)
cdef void apply_matrix(double [:,:] M, double[:] v):
    cdef double[3] res
    cdef int i, j
    
    for i in range(3):
        res[i] = 0
    
    for i in range(3):
        for j in range(3):
          res[i] += M[i, j] * v[j]
    
    for i in range(3):
        v[i] = res[i]

cdef void mat3_transpose(double [:, :] M):
        cdef double tmp
        cdef int i, j
        
        for i in range(3):
            for j in range(3):
                tmp = M[i, j]
                M[i, j] = M[j, i]
                M[j, i] = tmp



@cython.boundscheck(False)
@cython.cdivision(True)
def fast_cylinder_translate(reference_verts, reference_norms,
                            np.ndarray bounds, radii, lengths):
    '''Optimization of cylinder renderer

    '''
    cdef int i, ii, j, ind, k
    cdef int ncyl = len(bounds)
    cdef int nverts = len(reference_verts)
    
    cdef double[:] sme = np.array([0.0, 0.0, 0.0])
    cdef double[:] s, e
    cdef double[:] z_axis = np.array([0.0, 0.0, 1.0]), zero_axis = np.zeros(3)
    cdef double[:] axis = np.array([0.0, 0.0, 0.0])
    cdef double ang, nm
    cdef double[:] tmpv

    cdef double[:, :] rot = np.zeros((3,3))
    cdef double[:] radiibuf = np.array(radii)
    cdef double[:] lengthsbuf = np.array(lengths)

    vertices = np.tile(reference_verts, (ncyl, 1))
    cdef double[:, :] vertbuf = vertices
    normals = np.tile(reference_norms, (ncyl, 1))
    cdef double[:, :] normbuf = normals
    
    for i in range(ncyl):
        s = bounds[i, 0]
        e = bounds[i, 1]
        
        # Scale the radii and the length
        #vrt = reference_verts.copy()

        for j in range(nverts):
            ind = i*nverts + j
            vertbuf[ind, 0] *= radiibuf[i]
            vertbuf[ind, 1] *= radiibuf[i]            
            vertbuf[ind, 2] *= lengthsbuf[i]
        
        # Generate rotation matrix
        # Special case, if the axis is the z-axis
        vec3_sub(e, s, sme)
        
        ang = angle_between_vectors(z_axis, sme)
        vector_product(z_axis, sme, axis)

        if ang==0 or allclose_d(axis, zero_axis):
            rot = np.eye(3)
        else:
            nm = norm(axis)
            for ii in range(3):
                axis[ii] = axis[ii] / nm
            
            rotation_matrix(ang, axis, rot)
        
        for j in range(nverts):
            apply_matrix(rot.T, vertbuf[i*nverts + j])
            for k in range(3):
                vertbuf[i*nverts + j, k] += e[k]
            
            apply_matrix(rot.T, normbuf[i*nverts + j])
            
    return vertices, normals