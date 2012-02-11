"""trackball_camera.py - An OpenGL Trackball Camera Class for Pyglet

by Roger Allen, July 2008
roger@rogerandwendy.com

A class for simple-minded 3d example apps.

Usage:

Initialize with a radius from the center/focus point:

   tbcam = TrackballCamera(5.0)

After adjusting your projection matrix, set the modelview matrix.

   tbcam.update_modelview()

On each primary mouse click, scale the x & y to [-1,1] and call:

   tbcam.mouse_roll(x,y,False)

On each primary mouse drag, scale the x & y to [-1,1] and call:

   tbcam.mouse_roll(x,y)

Mouse movements adjust the modelview projection matrix directly.

"""

__version__ = "1.0"

# Code derived from the GLUT trackball.c, but now quite different and
# customized for pyglet.
#
# I simply wanted an easy-to-use trackball camera for quick-n-dirty
# opengl programs that I'd like to write.  Finding none, I grabbed
# the trackball.c code & started hacking.
#
# Originally implemented by Gavin Bell, lots of ideas from Thant Tessman
# and the August '88 issue of Siggraph's "Computer Graphics," pp. 121-129.
# and David M. Ciemiewicz, Mark Grossman, Henry Moreton, and Paul Haeberli
#
# Note: See the following for more information on quaternions:
# 
# - Shoemake, K., Animating rotation with quaternion curves, Computer
#   Graphics 19, No 3 (Proc. SIGGRAPH'85), 245-254, 1985.
# - Pletinckx, D., Quaternion calculus as a basic tool in computer
#   graphics, The Visual Computer 5, 2-13, 1989.
#
# Gavin Bell's code had this copyright notice:
# (c) Copyright 1993, 1994, Silicon Graphics, Inc.
# ALL RIGHTS RESERVED
# Permission to use, copy, modify, and distribute this software for
# any purpose and without fee is hereby granted, provided that the above
# copyright notice appear in all copies and that both the copyright notice
# and this permission notice appear in supporting documentation, and that
# the name of Silicon Graphics, Inc. not be used in advertising
# or publicity pertaining to distribution of the software without specific,
# written prior permission.
# 
# THE MATERIAL EMBODIED ON THIS SOFTWARE IS PROVIDED TO YOU "AS-IS"
# AND WITHOUT WARRANTY OF ANY KIND, EXPRESS, IMPLIED OR OTHERWISE,
# INCLUDING WITHOUT LIMITATION, ANY WARRANTY OF MERCHANTABILITY OR
# FITNESS FOR A PARTICULAR PURPOSE.  IN NO EVENT SHALL SILICON
# GRAPHICS, INC.  BE LIABLE TO YOU OR ANYONE ELSE FOR ANY DIRECT,
# SPECIAL, INCIDENTAL, INDIRECT OR CONSEQUENTIAL DAMAGES OF ANY
# KIND, OR ANY DAMAGES WHATSOEVER, INCLUDING WITHOUT LIMITATION,
# LOSS OF PROFIT, LOSS OF USE, SAVINGS OR REVENUE, OR THE CLAIMS OF
# THIRD PARTIES, WHETHER OR NOT SILICON GRAPHICS, INC.  HAS BEEN
# ADVISED OF THE POSSIBILITY OF SUCH LOSS, HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, ARISING OUT OF OR IN CONNECTION WITH THE
# POSSESSION, USE OR PERFORMANCE OF THIS SOFTWARE.
# 
# US Government Users Restricted Rights
# Use, duplication, or disclosure by the Government is subject to
# restrictions set forth in FAR 52.227.19(c)(2) or subparagraph
# (c)(1)(ii) of the Rights in Technical Data and Computer Software
# clause at DFARS 252.227-7013 and/or in similar or successor
# clauses in the FAR or the DOD or NASA FAR Supplement.
# Unpublished-- rights reserved under the copyright laws of the
# United States.  Contractor/manufacturer is Silicon Graphics,
# Inc., 2011 N.  Shoreline Blvd., Mountain View, CA 94039-7311.
                                
import math
import copy
from pyglet.gl import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# a little vector library that is misused in odd ways below.
def v3add(src1, src2):
    return [ src1[0] + src2[0],
             src1[1] + src2[1],
             src1[2] + src2[2] ]

def v3sub(src1, src2):
    return [ src1[0] - src2[0],
             src1[1] - src2[1],
             src1[2] - src2[2] ]

def v3scale(v, scale):
    return [ v[0] * scale,
             v[1] * scale,
             v[2] * scale ]

def v3dot(v1, v2):
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]

def v3cross(v1, v2):
    return [ (v1[1] * v2[2]) - (v1[2] * v2[1]),
             (v1[2] * v2[0]) - (v1[0] * v2[2]),
             (v1[0] * v2[1]) - (v1[1] * v2[0]) ]

def v3length(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])

def v3normalize(v):
    try:
        tmp = v3scale(v,1.0/v3length(v))
        return tmp
    except ZeroDivisionError:
        return v

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Some quaternion routines
def q_add(q1, q2):
    """Given two quaternions, add them together to get a third quaternion.
    Adding quaternions to get a compound rotation is analagous to adding
    translations to get a compound translation.  When incrementally
    adding rotations, the first argument here should be the new rotation.
    """
    t1 = v3scale(q1,q2[3])
    t2 = v3scale(q2,q1[3])
    t3 = v3cross(q2,q1)
    tf = v3add(t1,t2)
    tf = v3add(t3,tf)
    tf.append( q1[3] * q2[3] - v3dot(q1,q2) )
    return tf

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def q_from_axis_angle(a, phi):
    # a is a 3-vector, q is a 4-vector
    """Computes a quaternion based on an axis (defined by the given vector)
    and an angle about which to rotate.  The angle is expressed in radians.
    """
    q = v3normalize(a)
    q = v3scale(q, math.sin(phi/2.0))
    q.append(math.cos(phi/2.0))
    return q

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def q_normalize(q):
    """Return a normalized quaternion"""
    mag = (q[0]*q[0] + q[1]*q[1] + q[2]*q[2] + q[3]*q[3])
    if mag != 0:
        for i in range(4): 
            q[i] /= mag;
    return q

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def q_matrix(q):
    """return the rotation matrix based on q"""
    m = [0.0]*16
    m[0*4+0] = 1.0 - 2.0 * (q[1] * q[1] + q[2] * q[2])
    m[0*4+1] = 2.0 * (q[0] * q[1] - q[2] * q[3])
    m[0*4+2] = 2.0 * (q[2] * q[0] + q[1] * q[3])
    m[0*4+3] = 0.0

    m[1*4+0] = 2.0 * (q[0] * q[1] + q[2] * q[3])
    m[1*4+1] = 1.0 - 2.0 * (q[2] * q[2] + q[0] * q[0])
    m[1*4+2] = 2.0 * (q[1] * q[2] - q[0] * q[3])
    m[1*4+3] = 0.0

    m[2*4+0] = 2.0 * (q[2] * q[0] - q[1] * q[3])
    m[2*4+1] = 2.0 * (q[1] * q[2] + q[0] * q[3])
    m[2*4+2] = 1.0 - 2.0 * (q[1] * q[1] + q[0] * q[0])
    m[2*4+3] = 0.0

    m[3*4+0] = 0.0
    m[3*4+1] = 0.0
    m[3*4+2] = 0.0
    m[3*4+3] = 1.0
    return m

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def project_z(r, x, y):
    """Project an x,y pair onto a sphere of radius r OR a hyperbolic sheet
    if we are away from the center of the sphere.
    """
    d = math.sqrt(x*x + y*y)
    if (d < r * 0.70710678118654752440):    # Inside sphere
        z = math.sqrt(r*r - d*d)
    else:                                   # On hyperbola
        t = r / 1.41421356237309504880
        z = t*t / d
    return z

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Trackball Camera Class
#
class TrackballCamera:
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, radius=1.0):
        """ initialize the camera, giving a radius from the focal point for
        the camera eye.  Update focal point & up via the update_modelview call.
        """
        # the quaternion storing the rotation
        self.rot_quat = [0,0,0,1]
        # the last mouse update
        self.last_x = None
        self.last_y = None
        # camera vars
        self.cam_eye   = [0.,0.,radius]
        self.cam_focus = [0.,0.,0.]
        self.cam_up    = [0.,1.,0.]
        # in add_quat routine, renormalize "sometimes"
        self.RENORMCOUNT = 97
        self.count = 0
        # Trackballsize should really be based on the distance from the center of
        # rotation to the point on the object underneath the mouse.  That
        # point would then track the mouse as closely as possible.  This is a
        # simple example, though, so that is left as an Exercise for the
        # Programmer.
        self.TRACKBALLSIZE = 0.8

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def mouse_roll(self, norm_mouse_x, norm_mouse_y, dragging=True):
        """When you click or drag the primary mouse button, scale the mouse
        x & y to the range [-1.0,1.0] and call this routine to roll the trackball
        and update the modelview matrix.
        
        The initial click should set dragging to False.
        """
        if dragging:
            norm_mouse_quat = self._rotate(norm_mouse_x, norm_mouse_y)
            self.rot_quat  = q_add(norm_mouse_quat,self.rot_quat)
            self.count += 1
            if (self.count > self.RENORMCOUNT):
                self.rot_quat = q_normalize(self.rot_quat)
                self.count = 0
            self.update_modelview()
        self.last_x = norm_mouse_x
        self.last_y = norm_mouse_y

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def mouse_zoom(self, norm_mouse_x, norm_mouse_y, dragging=True):
        """When you click or drag a secondary mouse button, scale the mouse
        x & y to the range [-1.0,1.0] and call this routine to change the
        trackball's camera radius and update the modelview matrix.
        
        The initial click should set dragging to False.        
        """
        if self.last_x:
            dx = norm_mouse_x - self.last_x
            dy = norm_mouse_y - self.last_y
            norm_mouse_r_delta = 20.0*math.sqrt(dx*dx+dy*dy)
            if dy > 0.0:
                norm_mouse_r_delta = -norm_mouse_r_delta
            if dragging:
                self.cam_eye[2] = self.cam_eye[2] + norm_mouse_r_delta
                if self.cam_eye[2] < 1.0:
                    self.cam_eye[2] == 1.0
                self.update_modelview()
        self.last_x = norm_mouse_x
        self.last_y = norm_mouse_y

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def update_modelview(self,cam_radius=None,cam_focus=None,cam_up=None):
        """Given a radius for the trackball camera, a focus-point 3-vector,
        another 3-vector the points 'up' combined with the current
        orientation of the trackball, update the GL_MODELVIEW matrix.
        """
        if cam_radius:
            self.cam_eye[2] = cam_radius
        if cam_focus:
            self.cam_focus = cam_focus
        if cam_up:
            self.cam_up = cam_up
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(
            self.cam_eye[0],self.cam_eye[1],self.cam_eye[2],
            self.cam_focus[0],self.cam_focus[1],self.cam_focus[2],
            self.cam_up[0],self.cam_up[1],self.cam_up[2]
            )
        # rotate this view by the current orientation
        m = self._matrix()
        mm = (GLfloat * len(m))(*m)  # FIXME there is prob a better way...
        glMultMatrixf(mm)
        
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _matrix(self):
        """return the rotation matrix for the trackball"""
        return q_matrix(self.rot_quat)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _rotate(self, norm_mouse_x, norm_mouse_y): 
        """Pass the x and y coordinates of the last and current positions of
        the mouse, scaled so they are in the range [-1.0,1.0].
        
        Simulate a track-ball.  Project the points onto the virtual
        trackball, then figure out the axis of rotation, which is the cross
        product of LAST NEW and O LAST (O is the center of the ball, 0,0,0)
        Note:  This is a deformed trackball-- is a trackball in the center,
        but is deformed into a hyperbolic sheet of rotation away from the
        center.  This particular function was chosen after trying out
        several variations.
        """
        # handle special case
        if (self.last_x == norm_mouse_x and self.last_y == norm_mouse_y):
            # Zero rotation 
            return [ 0.0, 0.0, 0.0, 1.0]

        #
        # First, figure out z-coordinates for projection of P1 and P2 to
        # deformed sphere
        #
        last = [self.last_x, self.last_y, project_z(self.TRACKBALLSIZE,self.last_x,self.last_y)]
        new  = [norm_mouse_x, norm_mouse_y, project_z(self.TRACKBALLSIZE,norm_mouse_x,norm_mouse_y)]

        #
        # Now, we want the cross product of LAST and NEW
        # aka the axis of rotation
        #
        a = v3cross(new,last)
        
        #
        # Figure out how much to rotate around that axis (phi)
        #
        d = v3sub(last,new)
        t = v3length(d) / (2.0*self.TRACKBALLSIZE)
        # Avoid problems with out-of-control values...
        if (t > 1.0): t = 1.0
        if (t < -1.0): t = -1.0
        phi = 2.0 * math.asin(t)

        return q_from_axis_angle(a,phi)

