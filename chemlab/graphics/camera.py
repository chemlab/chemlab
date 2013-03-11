'''Module to provide a nice camera for 3d applications'''
from .gletools.transformations import rotation_matrix, translation_matrix
from .gletools.transformations import simple_clip_matrix, clip_matrix


import numpy as np
import numpy.linalg as LA

class Camera:
    
    def __init__(self):
        self.position = np.array([0.0, 0.0, 5.0]) # Position in real coordinates
        
        
        self.pivot = np.array([0.0, 0.0, 0.0])
        
        # Perspective parameters
        self.scale = 1.0
        self.aspectratio = 1.0
        self.z_near = 0.1
        self.z_far = 100.0
        
        # Those are the direction fo the three axis of the camera in
        # world coordinates, used to compute the rotations necessary
        self.a = np.array([1.0, 0.0, 0.0])
        self.b = np.array([0.0, 1.0, 0.0])
        self.c = np.array([0.0, 0.0, -1.0])
        
    def orbit_y(self, angle):
        
        # Subtract pivot point
        self.position -= self.pivot
        
        # Rotate
        rot = rotation_matrix(-angle, self.b)[:3,:3]
        self.position = np.dot(rot, self.position)
        
        # Add again the pivot point
        self.position += self.pivot
        
        self.a = np.dot(rot, self.a)
        self.b = np.dot(rot, self.b)
        self.c = np.dot(rot, self.c)        
        
    def orbit_x(self, angle):
        # Subtract pivot point
        self.position -= self.pivot
        
        # Rotate
        rot = rotation_matrix(-angle, self.a)[:3,:3]
        self.position = np.dot(rot, self.position)
        
        # Add again the pivot point
        self.position += self.pivot
        
        self.a = np.dot(rot, self.a)
        self.b = np.dot(rot, self.b)
        self.c = np.dot(rot, self.c)        
        
    def _get_projection_matrix(self):
        # Matrix to convert from homogeneous coordinates to 
        # 2d coordinates args = (scale, znear, zfar, aspect_ratio)
        return simple_clip_matrix(self.scale, self.z_near,
                                  self.z_far, self.aspectratio)
        
    projection = property(_get_projection_matrix)
    
    def _get_matrix(self):
        rot = self._get_rotation_matrix()
        tra = self._get_translation_matrix()
        
        res = np.dot(rot, tra)        
        
        return res
    
    matrix = property(_get_matrix)
    
    def _get_translation_matrix(self):
        return translation_matrix(-self.position)
        
    def _get_rotation_matrix(self):
        # Rotate the system to bring it to 
        # coincide with 0, 0, -1
        a, b, c = self.a, self.b, self.c
        
        a0 = np.array([1.0, 0.0, 0.0])
        b0 = np.array([0.0, 1.0, 0.0])
        c0 = np.array([0.0, 0.0, -1.0])
        
        mfinal = np.array([a0, b0, c0]).T
        morig = np.array([a, b, c]).T
        
        mrot = np.dot(mfinal, morig.T)
        
        ret = np.eye(4)
        ret[:3,:3] = mrot
        return ret
        
    def unproject(self, x, y, z=-1.0):
        """Receive x and y as screen coordinates, between -1 and 1
        and returns a point in world coordinates. This is useful for
        picking. The z also goes from -1 to 1, where -1 is the
        "projection" plane, that is the plane nearest to us.
        
        """

        source = np.array([x,y,z,1.0])
    
        # Invert the combined matrix
        matrix = self.projection.dot(self.matrix)
        IM = LA.inv(matrix)
        res = np.dot(IM, source)
        
        return res[0:3]/res[3]

from .gletools.transformations import vector_product, angle_between_vectors

def map_to_arcball(x, y):
    # Find intersection between sphere and arcball

    # Sphere radius 3.0
    # the point of intersection is that:
    r = 1.0
    D = x*x + y*y
    rsq = r*r
    if D < rsq:
        z = (rsq - D)**0.5
    else: # Fallback on hyperbolic sheet
        z = (rsq/2.0) / D**0.5
        #z = 0.0
    
    return np.array([x,y,z])
    
def arcball(x, y, dx, dy, cam):
    start = map_to_arcball(x,y)
    end = map_to_arcball(x + dx, y + dy)

    start = cam.unproject(start[0], start[1], -start[2])
    end = cam.unproject(end[0], end[1], -end[2])
    
    axis = vector_product(end, start)
    angle = angle_between_vectors(end, start)
    
    # Sometimes when you go outside the window with the mouse
    # you get zero displacement, and therefore zero axis and zero
    # angle. This causes an error.
    if np.allclose(axis, np.zeros(3)) or np.equal(angle, 0.0):
        # Do not alter anything
        return
    
    rot = rotation_matrix(angle, axis)[:3, :3].T
    
    cam.position -= cam.pivot
    cam.position = rot.dot(cam.position)
    cam.position += cam.pivot
    
    cam.a = rot.dot(cam.a)
    cam.b = rot.dot(cam.b)
    cam.c = rot.dot(cam.c)