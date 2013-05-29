import numpy as np

from .base import AbstractRenderer
from .triangles import TriangleRenderer


class SphereRenderer(AbstractRenderer):
    '''Renders a set of spheres.

    The method used by this renderer is approximating a sphere by
    using triangles. While this is reasonably fast, for best
    performance and animation you should use
    :py:class:`~chemlab.graphics.renderers.SphereImpostorRenderer`
    
    .. image:: /_static/sphere_renderer.png
    
    **Parameters**

    widget:
        The parent ``QChemlabWidget``
    
    poslist: np.ndarray((NSPHERES, 3), dytpe=float)
        A position array. While there aren't dimensions, in the context
        of chemlab 1 unit of space equals 1 nm.
    
    radiuslist: np.ndarray(NSPHERES, dtype=float)
        An array with the radius of each sphere.
    
    colorlist: np.ndarray(NSPHERES, 4) or list of tuples
        An array with the color of each sphere. Suitable colors are
        those found in ``chemlab.graphics.colors`` or any
        tuple with values (r, g, b, a) in the range [0, 255]
    
    '''

    def __init__(self, widget, poslist, radiuslist, colorlist, shading='phong'):
        
        self.viewer = widget

        self.poslist = poslist
        self.radiuslist = radiuslist
        self.colorlist = colorlist
        self.n_spheres = len(poslist)
        
        
        # Initialize a sphere object with radius 1 that contains our
        # triangles. We use that to generate the vertices and normals
        _SPHERE_MRES = Sphere(1.0, np.array([0.0, 0.0, 0.0]), parallels=10, meridians=15)
        
        sp_verts = _SPHERE_MRES.tri_vertex.astype(np.float32)
        sp_norms = _SPHERE_MRES.tri_normals.astype(np.float32)
        
        verts_one_sphere = len(sp_verts)
        

        # To produce a general sphere from a sphere radius 1 centered
        # in origin, we have to multiply each vertex of the sphere by the radius
        # and then translate that by the position of the sphere

        # We do that in a tight numpy operation
        self.sp_verts = sp_verts#reshape((sp_verts.shape[0]/3, 3))
        
        # Correct
        sphs_verts = np.tile(self.sp_verts, self.n_spheres)
        sphs_verts = sphs_verts.reshape((self.n_spheres, len(self.sp_verts)/3, 3))
        
        sphs_verts *= np.array(radiuslist).reshape(self.n_spheres, 1, 1)
        self.sphs_verts_radii = sphs_verts.copy()
        sphs_verts += np.array(poslist).reshape(self.n_spheres, 1, 3)
        
        self._n_triangles = len(sp_verts)/3 * self.n_spheres
        
        vertices = sphs_verts
        
        
        normals = np.tile(sp_norms, self.n_spheres)
        colors_ = np.repeat(colorlist, verts_one_sphere/3, axis=0)


        self.tr = TriangleRenderer(widget, vertices.flatten(),
                                   normals.flatten(), colors_, shading=shading)
    
    def draw(self):
        self.tr.draw()

    def update_positions(self, positions):
        '''Update the sphere positions.
        '''
        sphs_verts = self.sphs_verts_radii.copy()
        sphs_verts += positions.reshape(self.n_spheres, 1, 3)

        self.tr.update_vertices(sphs_verts)
        self.poslist = positions
        
    def update_colors(self, colorlist):
        
        self.tr.update_colors(colorlist)

from ..transformations import distance, normalized

class Sphere(object):
    def __init__(self, radius, center, parallels=20, meridians=15, color=[0.0, 0.0, 0.0, 0.0]):
        '''Create a Sphere object specifying its radius its center point. You can modulate its smoothness using the
        parallel and meridians settings.

        '''
        self.radius = radius
        self.center = center
        self.parallels = parallels
        self.meridians = meridians
        self.color = color
        
        self.vertices = []
        self.indices = []
        self.normals = []

        self.tri_vertex = []
        self.tri_color = []
        self.tri_normals = []
        
        self.update_vlist = False
        self._generate_vertices()

    def _generate_vertices(self):
        # Tip of the sphere
        tip = np.array([0.0, 0.0, self.radius])
        # Bottom of the sphere
        bottom = np.array([0.0, 0.0, -self.radius])
        
        dphi = np.pi/self.parallels 
        dtheta = 2*np.pi/self.meridians
        
        self.vertices.append(tip)
        for j in range(1, self.parallels):
            point_z = self.radius*np.cos(dphi*j)
            for i in range(self.meridians+1):
                point_x = np.sin(dphi*j)*np.cos(i*dtheta)*self.radius
                point_y = np.sin(dphi*j)*np.sin(i*dtheta)*self.radius
                self.vertices.append(np.array([point_x, point_y, point_z]))
        self.vertices.append(bottom)
        
        
        self.vertices = np.array(self.vertices)

        # Normals, this is quite easy since they are the vertices
        for vertex in self.vertices:
            self.normals.append(normalized(vertex))
        self.normals = np.array(self.normals) # Numpyize
        
        # Translate the sphere
        for i, vertex in enumerate(self.vertices):
            self.vertices[i] -= self.center 

        # Generating triangles!!
        # Draw each triangle in order to form the sphere
        m = self.meridians
        
        # Cap of the sphere
        cap_i = [np.array([0, 1, 2]) + np.array([0, 1, 1])*i for i in range(m)] # Up to the last point minus 1
        cap_i = np.array(cap_i).flatten()
        indexed = cap_i
        
        # Body of the sphere
        for k in range(self.parallels-2):
            offset = 1 + k*(m+1)
            body_0 = offset + np.array([0, m+1, 1, 1, m + 1, m + 2]) # first two triangles
            body_i = np.concatenate([body_0 + i for i in range(m)])
            indexed = np.concatenate((indexed, body_i))
        
        # Bottom of the sphere
        offset += m

        last = len(self.vertices) - 1
        bot_i = [np.array([last, 1 + offset, 2 + offset]) +
                 np.array([0, 1, 1])*i for i
                 in range(m)]
        indexed = np.concatenate((indexed, np.array(bot_i).flatten()))
        self.tri_vertex = self.vertices[indexed].flatten()
        self.tri_normals = self.normals[indexed].flatten()

        self.tri_n = len(indexed)
        self.tri_color = self.tri_n * self.color
        
        
    def rotate(self, axis, angle):
        rotmat = rotation_matrix( angle,axis)[:3,:3]
        
        # Rototranslate the vertices and others
        for i, vertex in enumerate(self.vertices):
            self.vertices[i] = np.dot(rotmat, vertex - self.center) + self.center
            self.normals[i] = np.dot(rotmat, self.normals[i])
