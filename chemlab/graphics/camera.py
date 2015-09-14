'''Module to provide a nice camera for 3d applications'''
from .transformations import rotation_matrix, translation_matrix
from .transformations import simple_clip_matrix, clip_matrix
from .transformations import vector_product, angle_between_vectors, normalized
from ..utils import fequal 

import numpy as np
import numpy.linalg as LA

class Camera:
    """Our viewpoint on the 3D world. The Camera class can be used to
    access and modify from which point we're seeing the scene.

    It also handle the projection matrix (the matrix we apply to
    project 3d points onto our 2d screen).
    
    .. py:attribute:: position
       
       :type: np.ndarray(3, float)
       :default: np.array([0.0, 0.0, 5.0])
    
       The position of the camera. You can modify this attribute to
       move the camera in various directions using the absoule x, y
       and z coordinates.
    
    .. py:attribute:: a, b, c
       
       :type: np.ndarray(3), np.ndarray(3), np.ndarray(3) dtype=float
       :default: a: np.ndarray([1.0, 0.0, 0.0])
                 b: np.ndarray([0.0, 1.0, 0.0])
                 c: np.ndarray([0.0, 0.0, -1.0])

       Those three vectors represent the camera orientation. The ``a``
       vector points to our right, the ``b`` points upwards and ``c``
       in front of us.
    
       By default the camera points in the negative z-axis
       direction.

    .. py:attribute:: pivot

       :type: np.ndarray(3, dtype=float)
       :default: np.array([0.0, 0.0, 0.0])
    
       The point we will orbit around by using
       :py:meth:`Camera.orbit_x` and :py:meth:`Camera.orbit_y`.
       
    .. py:attribute:: matrix

       :type: np.ndarray((4,4), dtype=float)
       
       Camera matrix, it contains the rotations and translations
       needed to transform the world according to the camera position.
       It is generated from the ``a``,``b``,``c`` vectors.
    
    .. py:attribute:: projection

       :type: np.ndarray((4, 4),dtype=float)
       
       Projection matrix, generated from the projection parameters.
    
    .. py:attribute:: z_near, z_far
       
       :type: float, float
    
       Near and far clipping planes. For more info refer to:
       http://www.lighthouse3d.com/tutorials/view-frustum-culling/
    
    .. py:attribute:: fov
       
       :type: float
    
       field of view in degrees used to generate the projection matrix.
    
    .. py:attribute:: aspectratio

       :type: float
        
       Aspect ratio for the projection matrix, this should be adapted
       when the application window is resized.

    """

    def __init__(self):
        self.position = np.array([0.0, 0.0, 5.0]) # Position in real coordinates
        
        self.pivot = np.array([0.0, 0.0, 0.0])
        
        # Perspective parameters
        self.fov = 45.0
        self.aspectratio = 1.0
        self.z_near = 0.5
        self.z_far = 500.0
        
        # Those are the direction fo the three axis of the camera in
        # world coordinates, used to compute the rotations necessary
        self.a = np.array([1.0, 0.0, 0.0])
        self.b = np.array([0.0, 1.0, 0.0])
        self.c = np.array([0.0, 0.0, -1.0])
        
    def orbit_y(self, angle):
        '''Orbit around the point ``Camera.pivot`` by the angle
        *angle* expressed in radians. The axis of rotation is the
        camera "right" vector, ``Camera.a``.

        In practice, we move around a point like if we were on a Ferris
        wheel.

        '''
        
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
        '''Same as :py:meth:`~chemlab.graphics.camera.Camera.orbit_y`
        but the axis of rotation is the :py:attr:`Camera.b` vector.
        
        We rotate around the point like if we sit on the side of a salad
        spinner.

        '''
        
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
        
    def mouse_rotate(self, dx, dy):
        '''Convenience function to implement the mouse rotation by
        giving two displacements in the x and y directions.

        '''
        fact = 1.5
        self.orbit_y(-dx*fact)
        self.orbit_x(dy*fact)

    def mouse_zoom(self, inc):
        '''Convenience function to implement a zoom function.

        This is achieved by moving ``Camera.position`` in the
        direction of the ``Camera.c`` vector.

        '''
        # Square Distance from pivot
        dsq = np.linalg.norm(self.position - self.pivot)
        minsq = 1.0**2  # How near can we be to the pivot
        maxsq = 7.0**2 # How far can we go 

        scalefac = 0.25

        if dsq > maxsq and inc < 0: 
            # We're going too far
            pass
        elif dsq < minsq and inc > 0:
            # We're going too close
            pass
        else:
            # We're golden
            self.position += self.c*inc*scalefac

    def _get_projection_matrix(self):
        # Convert from homogeneous 3d coordinates to 
        # 2D coordinates
        
        fov = self.fov*np.pi/180.0
        
        top = np.tan(fov * 0.5)*self.z_near
        bottom = -top
        
        left = self.aspectratio * bottom
        right = self.aspectratio * top
        
        return clip_matrix(left, right, bottom, top,
                           self.z_near, self.z_far, perspective=True)
        
        
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
        """Receive x and y as screen coordinates and returns a point
        in world coordinates.

        This function comes in handy each time we have to convert a 2d
        mouse click to a 3d point in our space.

        **Parameters**
        
        x: float in the interval [-1.0, 1.0]
            Horizontal coordinate, -1.0 is leftmost, 1.0 is rightmost.
        
        y: float in the interval [1.0, -1.0]
            Vertical coordinate, -1.0 is down, 1.0 is up.
        
        z: float in the interval [1.0, -1.0]
            Depth, -1.0 is the near plane, that is exactly behind our
            screen, 1.0 is the far clipping plane.
        
        :rtype: np.ndarray(3,dtype=float)
        :return: The point in 3d coordinates (world coordinates).
        
        """

        source = np.array([x,y,z,1.0])
    
        # Invert the combined matrix
        matrix = self.projection.dot(self.matrix)
        IM = LA.inv(matrix)
        res = np.dot(IM, source)
        
        return res[0:3]/res[3]

    def autozoom(self, points):
        '''Fit the current view to the correct zoom level to display
        all *points*.

        The camera viewing direction and rotation pivot match the
        geometric center of the points and the distance from that
        point is calculated in order for all points to be in the field
        of view. This is currently used to provide optimal
        visualization for molecules and systems

        **Parameters**
        
        points: np.ndarray((N, 3))
             Array of points.
        
        '''
        points = np.asarray(points)
        extraoff = 0.01
        
        # Project points on the plane defined by camera up and right
        # vector. This is achieved by using dot product on camera a
        # and b vectors
        abc = np.array([self.a, self.b, self.c])

        old_geom_center = points.sum(axis=0)/len(points)
        # Translate points
        points = points.copy() + self.position
        
        # Translate position to geometric_center along directions
        # a and b
        geom_center = points.sum(axis=0)/len(points)
        self.position += self.a * np.dot(geom_center, self.a)
        self.position += self.b * np.dot(geom_center, self.b)

        # Translate pivot to the geometric center
        self.pivot = old_geom_center
        
        # Get the bounding sphere radius by searching for the most
        # distant point
        bound_radius = np.sqrt(((points-geom_center) * (points-geom_center)).sum(axis=1).max())

        # Calculate the distance in order to have the most distant
        # point in our field of view (top/bottom)
        fov_topbottom = self.fov*np.pi/180.0
        
        dist = (bound_radius + self.z_near)/np.tan(fov_topbottom * 0.5)
        
        # Set the c-component of the position at the calculated distance
        # 1) translate the position on the pivot
        self.position = self.pivot.copy() 
        # 2) add the distance plus a little extra room
        self.position -= self.c * (dist*(1 + extraoff))

    def state(self):
        '''Return the current camera state as a dictionary, it can be
        restored with `Camera.restore`.

        '''
        return dict(a=self.a.tolist(), b=self.b.tolist(), c=self.c.tolist(),
                    pivot=self.pivot.tolist(), position=self.position.tolist())

    def restore(self, state):
        '''Restore the camera state, passed as a *state*
        dictionary. You can obtain a previous state from the method
        `Camera.state`.

        '''
        self.a = np.array(state['a']).copy()
        self.b = np.array(state['b']).copy()
        self.c = np.array(state['c']).copy()
        self.pivot = np.array(state['pivot']).copy()
        self.position = np.array(state['position']).copy()
