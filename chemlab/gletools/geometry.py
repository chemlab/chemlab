'''Geometry calculation utilities'''

import numpy as np
from numpy.linalg import norm

def normalized(x):
    '''Return the x vector normalized'''
    return x/norm(x)

def distance(x1, x2):
    '''Distance between two points in space
    '''
    return norm(x2 - x1)

def angle2v(x1, x2):
    '''Angle between two vectors'''
    return np.arccos(np.dot(x1, x2)/(norm(x1) * norm(x2)))

def rotation_matrix(direction, angle):
     """
     Create a rotation matrix corresponding to the rotation around a general
     axis by a specified angle.

     R = dd^T + cos(a) (I - dd^T) + sin(a) skew(d)

     Parameters:

         angle : float a
         direction : array d
     """
     d = np.array(direction, dtype=np.float64)
     d /= np.linalg.norm(d)

     eye = np.eye(3, dtype=np.float64)
     ddt = np.outer(d, d)
     skew = np.array([[    0,  d[2],  -d[1]],
                      [-d[2],     0,  d[0]],
                      [d[1], -d[0],    0]], dtype=np.float64)

     mtx = ddt + np.cos(angle) * (eye - ddt) + np.sin(angle) * skew
     return mtx
