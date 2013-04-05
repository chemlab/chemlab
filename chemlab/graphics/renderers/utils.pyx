# cython: profile=True
'''Speed utilities'''

import numpy as np
cimport numpy as np
from cython.view cimport array as cyarray
from ..transformations import (normalized,
                               unit_vector, distance,
                               rotation_matrix)


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
    
# cdef rotation_matrix(double angle, double[:] d, double[:, :] M):
#      """
#      Create a rotation matrix corresponding to the rotation around a general
#      axis by a specified angle.

#      R = dd^T + cos(a) (I - dd^T) + sin(a) skew(d)

#      Parameters:

#          angle : float a
#          direction : array d
#      """
#      cdef double cost = cos(angle)
#      cdef double sint = sin(angle)
#      cdef double ux, uy, uz
     
#      ux = d[0]
#      uy = d[1]
#      uz = d[2]
     
#      M[0, 0] = cost + ux*ux*(1-cost)
#      M[1, 0] = ux*uy*(1 - cost) - uz*sint
#      M[2, 0] = ux*uz*(1 - cost) + uy*sint
     
#      M[0, 1] = uy*ux*(1 - cost) + uz*sint
#      M[1, 1] = cost + uy*uy*(1 - cost)
#      M[2, 1] = uy*uz*(1-cost) - ux*sint

#      M[0, 2] = uz*ux*(1-cost) - uy*sint
#      M[1, 2] = uz*uy*(1-cost) + ux*sint
#      M[2, 2] = cost + uz*uz*(1-cost)
     
     

cdef void mat3_transpose(double [:, :] M):
        cdef double tmp
        cdef int i, j
        
        for i in range(3):
            for j in range(3):
                tmp = M[i, j]
                M[i, j] = M[j, i]
                M[j, i] = tmp
        
def fast_cylinder_translate(reference_verts, reference_norms,
                            np.ndarray bounds, radii, lengths):
    '''Optimization of cylinder renderer

    '''
    vertices = []
    normals = []
    cdef int i, ii
    cdef int ncyl = len(bounds)
    cdef double[:] s, e, sme = np.array([0.0, 0.0, 0.0])
    cdef double[:] z_axis = np.array([0.0, 0.0, 1.0])
    cdef double[:] axis = np.array([0.0, 0.0, 0.0])
    cdef double ang

    cdef double[:, :] rot = np.zeros((3,3))
    
    for i in range(ncyl):
        s = bounds[i][0]
        e = bounds[i][1]
        
        # Scale the radii and the length
        vrt = reference_verts.copy()
        vrt[:, 0:2] *= radii[i]
        vrt[:, 2] *= lengths[i]

        # Generate rotation matrix

        # Special case, if the axis is the z-axis
        vec3_sub(e, s, sme)
        ang = angle_between_vectors(z_axis, sme)
        vector_product(z_axis, sme, axis)

        if ang==0 or allclose_d(axis, np.array([0.0, 0.0, 0.0])):
            rot = np.eye(3)
        else:
            for ii in range(3):
                axis[ii] = axis[ii]/norm(axis)
            #rotation_matrix(ang, axis, rot)
            rot = rotation_matrix(ang, axis)[:3,:3]

        vertices.extend(np.dot(vrt, rot) + e)
        normals.extend(np.dot(reference_norms, rot))

    return vertices, normals