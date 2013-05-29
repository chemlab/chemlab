import numpy as np
from ..transformations import (rotation_matrix, normalized,
                               angle_between_vectors, unit_vector, distance,
                               vector_product)
from .triangles import TriangleRenderer
from .point import PointRenderer
from .base import AbstractRenderer

from .utils import fast_cylinder_translate


class CylinderRenderer(AbstractRenderer):
    '''Renders a set of cylinders.
        
    The API is quite similar to
    :py:class:`~chemlab.graphics.renderers.LineRenderer`
    
    .. image:: /_static/cylinder_renderer.png
    
    **Parameters**
    
    widget:
        The parent QChemlabWidget
    bounds: np.ndarray((NCYL, 2, 3), dtype=float)
        Start and end points of the cylinder.
    colors: np.ndarray((NYCL, 4), dtype=np.uint8)
        The color for each cylinder.
    
    '''
    def __init__(self, widget, bounds, radii, colors):
        self.bounds = bounds
        self.radii = radii
        self.colors = colors
        
        
        starts =  bounds[:,0,:]
        ends = bounds[:,1,:]
        
        self.lengths = lengths = np.sqrt(((ends - starts)**2).sum(axis=1))
        
        # Unit cylinder
        cyl = Cylinder(1.0, np.array([0.0, 0.0, 0.0]),
                       np.array([0.0, 0.0, 1.0]))
        
        self._reference_verts = cyl.tri_vertex
        self._reference_norms = cyl.tri_normals
        
        n_v = len(self._reference_verts)
        self._reference_verts = self._reference_verts.reshape(n_v/3, 3)
        self._reference_norms = self._reference_norms.reshape(n_v/3, 3)
        
        self._reference_n = len(self._reference_verts)
        
        self.n_cylinders = len(bounds)
        
        vertices, normals, colors = self._process_reference()
        
        self.tr = TriangleRenderer(widget, vertices,  normals, colors)
        
    def draw(self):
        self.tr.draw()

    def _process_reference(self):
        import time
        t0 = time.time()
        vertices, normals = fast_cylinder_translate(self._reference_verts, self._reference_norms,
                                                    self.bounds, self.radii, self.lengths)
        
        colors = np.repeat(self.colors, self._reference_n, axis=0)
        return vertices, normals, colors
        
    def update_bounds(self, bounds):
        '''Update cylinders start and end positions

        '''
        starts =  bounds[:,0,:]
        ends = bounds[:,1,:]

        self.bounds = bounds
        self.lengths =  np.sqrt(((ends - starts)**2).sum(axis=1))
        
        vertices, normals, colors = self._process_reference()
        
        self.tr.update_vertices(vertices)
        self.tr.update_normals(normals)
        
        
from ..colors import purple        
class Cylinder(object):
    def __init__(self, radius, start, end, cloves=10, color=purple):
        '''Create a Cylinder object specifying its radius its start
        and end points. You can modulate its smoothness using the
        "cloves" settings.

        '''
        self.radius = radius
        self.start = start
        self.end = end
        self.axis = unit_vector(end - start)
        self.cloves = cloves
        self.color = color
        
        self.vertices = []
        self.indices = []
        self.normals = []
        
        self.tri_color = self.color*self.cloves*2*3
        self.tri_vertex = []
        self.tri_normals = []
        
        self._generate_vertices()

    def _generate_vertices(self):
        # Generate a cylinder centered at axis 0
        length = distance(self.start, self.end)
        
        # First two points
        self.vertices.append(np.array([self.radius, 0.0, 0.0]))
        self.vertices.append(np.array([self.radius, 0.0, length]))
        
        z_axis = np.array([0.0, 0.0, 1.0])
        for i in range(1, self.cloves):
            rotmat = rotation_matrix( i * 2*np.pi/self.cloves, z_axis)[:3,:3]
            
            nextbottom = np.dot(rotmat, self.vertices[0])
            nextup = np.dot(rotmat, self.vertices[1])
            self.vertices.append(nextbottom)
            self.vertices.append(nextup)
        
        # Last two points
        self.vertices.append(np.array([self.radius, 0.0, 0.0]))
        self.vertices.append(np.array([self.radius, 0.0, length]))
        
        self.vertices = np.array(self.vertices)
        self.indices = range(len(self.vertices.flatten()))
        
        # Normals, this is quite easy they are the coordinate with
        # null z
        for vertex in self.vertices:
            self.normals.append(normalized(np.array([vertex[0], vertex[1], 0.0])))
        self.normals = np.array(self.normals) # Numpyize
        
        ang = angle_between_vectors(z_axis, self.axis)
        
        if np.allclose(z_axis, self.axis):
            # Special case
            rotmat = np.eye(3)
        else:
            rotmat = rotation_matrix(-ang,
                                     vector_product(z_axis, self.axis))[:3,:3]
            
        
        # Rototranslate the cylinder to the real axis
        self.vertices = np.dot(self.vertices, rotmat.T) - self.end
        self.normals = np.dot(self.normals, rotmat.T)
        # for i, vertex in enumerate(self.vertices):
        #     self.vertices[i] = np.dot(rotmat, vertex) - self.start
        #     self.normals[i] = np.dot(rotmat, self.normals[i])
        
        # Now for the indices let's generate triangle stuff
        n = self.cloves * 2 + 2
        # Draw each triangle in order to form the cylinder
        a0 = np.array([0,1,2, 2,1,3]) # first two triangles
        a = np.concatenate([a0 + 2*i for i in range(self.cloves)])
        self.indices = a
        n = self.cloves * 2 * 3
        self.tri_vertex = self.vertices[a].flatten()
        self.tri_normals = self.normals[a].flatten()
        
