import numpy as np
from ..transformations import (rotation_matrix, normalized,
                               angle_between_vectors, unit_vector, distance,
                               vector_product)
from .triangles import TriangleRenderer
from .base import AbstractRenderer

class CylinderRenderer(AbstractRenderer):
    def __init__(self, viewer, bounds, radii, colors):
        '''Renders a set of cylinders. The starting and end point of
        each cylinder is stored in the startlist* and *endlist*.
        
        radius of cylinders are in *radiuslits*
        
        This renderer uses vertex array objects to deliver optimal
        performance.

        '''
        
        # Unit cylinder
        cyl = Cylinder(1.0, np.array([0.0, 0.0, 0.0]), np.array([0.0, 0.0, 1.0]))
        
        self._reference_verts = cyl.tri_vertex
        self._reference_norms = cyl.tri_normals
        
        n_v = len(self._reference_verts)
        self._reference_verts = self._reference_verts.reshape(n_v/3, 3)
        self._reference_norms = self._reference_norms.reshape(n_v/3, 3)
        
        self._reference_n = len(self._reference_verts)
        
        self.n_cylinders = len(bounds)
        
        # Rotate the cylinder
        vertices = []
        normals = []
        
        for s,e in bounds:
            # Generate rotation matrix
            ang = angle_between_vectors([0.0, 0.0, 1.0], e - s)
            axis = normalized(e - s)
            rot = rotation_matrix(ang, axis)[:3, :3]
            vertices.extend(np.dot(rot, self._reference_verts.T) + s[:,np.newaxis])
            normals.extend(np.dot(rot, self._reference_norms.T))
        
        vertices = np.array(vertices, dtype = np.float32)
        normals = np.array(normals, dtype = np.float32)
        colors = np.repeat(colors, self._reference_n * self.n_cylinders)
        
        self.tr = TriangleRenderer(viewer, vertices, colors, normals)
        
    def draw(self):
        self.tr.draw()
    
        
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
        self.indices = xrange(len(self.vertices.flatten()))

        # Normals, this is quite easy they are the coordinate with
        # null z
        for vertex in self.vertices:
            self.normals.append(normalized(np.array([vertex[0], vertex[1], 0.0])))
        
        self.normals = np.array(self.normals) # Numpyize
        
        ang = angle_between_vectors(z_axis, self.axis)
        rotmat = rotation_matrix(-ang, vector_product(z_axis, self.axis))[:3,:3]
        
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
        a = np.concatenate([a0 + 2*i for i in xrange(self.cloves)])
        self.indices = a
        n = self.cloves * 2 * 3
        self.tri_vertex = self.vertices[a].flatten()
        self.tri_normals = self.normals[a].flatten()
        
