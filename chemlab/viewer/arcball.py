from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import * # For cylinder primitive
from widget import GLUTWidget

import numpy as np
from numpy.linalg import norm

from math import sqrt, sin, cos
from quaternion import rotquat, rotmat


def normalized(x):
    """Return the vector *x* normalized.
    
    """
    return x/norm(x)

class ArcBall(object):
    
    def __init__(self):
        return

    def set_bounds(self, w, h):
        self.adjust_width = 1.0 / ((w)*0.5)
        self.adjust_height = 1.0/ ((h)*0.5)
    
    def set_initial_coords(self, x, y):
        #self.init_pos = self.get_sphere_position(x,y)
        self.init_pos = self._map_to_sphere(x, y)
        
    def set_final_coords(self, x, y):
        #self.end_pos = self.get_sphere_position(x,y)
        self.end_pos = self._map_to_sphere(x, y)


    def compute_optimal_radius(self, px, py, camera_position ):
        ## Move the camera
        glLoadIdentity()
        glTranslate(*camera_position)
        ## Compute the distance from the center to the corner of the
        ## screen at the z corresponding to the center of the viewport
        
        viewport = glGetIntegerv(GL_VIEWPORT)
        mvmatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        projmatrix = glGetDoublev(GL_PROJECTION_MATRIX)

        mp = gluProject(0.0, 0.0, 0.0, # Center of the object
                        mvmatrix,
                        projmatrix,
                        viewport)


        realy = viewport[3] -py -1
        r0 = gluUnProject(px, realy, mp[2], # side of the sphere
                          mvmatrix,
                          projmatrix,
                          viewport)
        r0 = np.array(r0)
        
        self.r = sqrt(r0.dot(r0))
        glLoadIdentity()
        

    def _map_to_sphere(self, x, y):
        a = np.zeros(3)
        b = np.zeros(3)
        
        b[0] = (x * self.adjust_width) - 1.0
        b[1] = 1.0- y * self.adjust_height

        length_sq = b.dot(b)
        if length_sq > 1.0:
            norm = 1.0/sqrt(length_sq)
            return b*norm
        else:
            newb = b.copy()
            newb[2] = sqrt(1.0 - length_sq)
            return newb
        
    def mouse_space_position(self, x, y):
        """Return two vectors, one corresponding to the world
        coordinates relative to the front (z=0) of the viewing area,
        and one of the bottom viewing area (z=1).

        """

        viewport = glGetIntegerv(GL_VIEWPORT)
        mvmatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        projmatrix = glGetDoublev(GL_PROJECTION_MATRIX)
        
        realy = viewport[3] -y -1

        x1, y1, z1 = gluUnProject(x, realy, 0.0,
        mvmatrix, projmatrix, viewport)
        P1 = np.array([x1,y1,z1]) # Initial point
        
        x2, y2, z2 = gluUnProject(x, realy, 1.0,
        mvmatrix, projmatrix, viewport)
        P2 = np.array([x2, y2, z2]) # Final point
        
        return P1, P2

    # def get_sphere_position(self, x, y):
    #     start, end = self.mouse_space_position(x,y)
        
    #     sphere_center = np.array([0.0, 0.0, 0.0])
        
    #     r = self.r
        
    #     x0, y0, z0 = start
    #     x1, y1, z1 = end
    #     xc, yc, zc = sphere_center
        
    #     # Quadratic eq Solution
    #     c = (x0-xc)**2 + (y0-yc)**2 + (z0-zc)**2 - r**2
    #     a = (x0-x1)**2 + (y0-y1)**2 + (z0-z1)**2
    #     b = a + c - (x1-xc)**2 - (y1-yc)**2 - (z1-zc)**2
    #     # Determinant for solution
    #     det = b**2 - 4*a*c
    #     if det>0:
    #         t1 = (-b + sqrt(det))/(2 * a)
    #         t2 = (-b - sqrt(det))/(2 * a)
    #         t = max(t1, t2)
            
    #         return start*(1-t) + t*end
    
    def get_rot_matrix(self):

        quat = np.zeros(4)
        # perpendicular vector
        perp = np.cross(self.init_pos, self.end_pos)
        perp_length = sqrt(perp.dot(perp))
        if perp_length > 1e-10:
            # nonzero vector
            quat[0] = perp[0]
            quat[1] = perp[1]
            quat[2] = perp[2]
            quat[3] = np.dot(self.init_pos, self.end_pos)
        else:
            # It's the zero quaternion
            pass
        
        mat = Matrix3fSetRotationFromQuat4f (quat)
        return mat
        
    def get_rot_axis_angle(self):
        axis = np.cross(normalized(self.init_pos),
                        normalized(self.end_pos))
        cos_angle = np.dot(normalized(self.init_pos),
                           normalized(self.end_pos))
        return axis, np.degrees(np.arccos(cos_angle))

def angle_axis_to_rot_matrix(angle, axis):
    angle = np.radians(angle)
    cost = cos(angle)
    sint = sin(angle)

    ux, uy, uz = axis
    return np.array([[cost + ux**2 * (1 - cost),
                      ux * uy * (1-cost) - uz*sint,
                      ux * uz * (1-cost) + uy*sint],
                     [uy * ux * (1 - cost) + uz*sint,
                       cost + uy**2 * (1 - cost),
                       uy * uz * (1 - cost) - ux * sint],
                     [uz * ux * (1 - cost) - uy * sint,
                      uz * uy * (1 - cost) + ux * sint,
                      cost + uz**2 * (1 - cost)]])


def Matrix3fSetIdentity ():
	return Numeric.identity (3, 'f')

def Matrix3fMulMatrix3f (matrix_a, matrix_b):
	return sumDot( matrix_a, matrix_b )




def Matrix4fSVD (NewObj):
	X = 0
	Y = 1
	Z = 2
	s = sqrt ( 
		( (NewObj [X][X] * NewObj [X][X]) + (NewObj [X][Y] * NewObj [X][Y]) + (NewObj [X][Z] * NewObj [X][Z]) +
		(NewObj [Y][X] * NewObj [Y][X]) + (NewObj [Y][Y] * NewObj [Y][Y]) + (NewObj [Y][Z] * NewObj [Y][Z]) +
		(NewObj [Z][X] * NewObj [Z][X]) + (NewObj [Z][Y] * NewObj [Z][Y]) + (NewObj [Z][Z] * NewObj [Z][Z]) ) / 3.0 )
	return s

def Matrix4fSetRotationScaleFromMatrix3f(NewObj, three_by_three_matrix):
	# Modifies NewObj in-place by replacing its upper 3x3 portion from the 
	# passed in 3x3 matrix.
	# NewObj = Matrix4fT ()
	NewObj [0:3,0:3] = three_by_three_matrix
	return NewObj

# /**
# * Sets the rotational component (upper 3x3) of this matrix to the matrix
# * values in the T precision Matrix3d argument; the other elements of
# * this matrix are unchanged; a singular value decomposition is performed
# * on this object's upper 3x3 matrix to factor out the scale, then this
# * object's upper 3x3 matrix components are replaced by the passed rotation
# * components, and then the scale is reapplied to the rotational
# * components.
# * @param three_by_three_matrix T precision 3x3 matrix
# */
def Matrix4fSetRotationFromMatrix3f (NewObj, three_by_three_matrix):
	scale = Matrix4fSVD (NewObj)

	NewObj = Matrix4fSetRotationScaleFromMatrix3f(NewObj, three_by_three_matrix);
	scaled_NewObj = NewObj * scale			 # Matrix4fMulRotationScale(NewObj, scale);
	return scaled_NewObj

def Matrix3fSetRotationFromQuat4f (q1):
	# Converts the H quaternion q1 into a new equivalent 3x3 rotation matrix. 
	X = 0
	Y = 1
	Z = 2
	W = 3

	NewObj = np.eye(3)
	n = np.dot(q1, q1)
	s = 0.0
	if (n > 0.0):
		s = 2.0 / n
	xs = q1 [X] * s;  ys = q1 [Y] * s;  zs = q1 [Z] * s
	wx = q1 [W] * xs; wy = q1 [W] * ys; wz = q1 [W] * zs
	xx = q1 [X] * xs; xy = q1 [X] * ys; xz = q1 [X] * zs
	yy = q1 [Y] * ys; yz = q1 [Y] * zs; zz = q1 [Z] * zs
	# This math all comes about by way of algebra, complex math, and trig identities.
	# See Lengyel pages 88-92
	NewObj [X][X] = 1.0 - (yy + zz);	NewObj [Y][X] = xy - wz; 			NewObj [Z][X] = xz + wy;
	NewObj [X][Y] =       xy + wz; 		NewObj [Y][Y] = 1.0 - (xx + zz);	NewObj [Z][Y] = yz - wx;
	NewObj [X][Z] =       xz - wy; 		NewObj [Y][Z] = yz + wx;          	NewObj [Z][Z] = 1.0 - (xx + yy)

	return NewObj
