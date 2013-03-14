'''3D drawing library for pyglet, it implements lots of drawing
shapes.

'''
# TODO clean this file, you have to setup better documented interfaces

import numpy as np
import pyglet
from geometry import distance, angle2v, normalized
from .transformations import rotation_matrix, angle_between_vectors, vector_product, unit_vector
from pyglet.graphics import draw

gray = (175, 175, 175)

class Shape:
    '''Encapsulate common methods between the shapes'''

    def translate(self, displacement):
        r = displacement
        for i,vertex in enumerate(self.vertices):
            self.vertices[i] -= r

class Cylinder(Shape):
    def __init__(self, radius, start, end, cloves=10, color=gray):
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
        
        self.vertex_list = pyglet.graphics.vertex_list(n,
                                                       ("v3f", self.tri_vertex),
                                                       ("n3f", self.tri_normals),
                                                       ("c3B", self.tri_color))

    def draw(self):
        self.vertex_list.draw(pyglet.gl.GL_TRIANGLES)
        # draw(self.cloves * 2 * 3, pyglet.gl.GL_TRIANGLES,
        #      ("v3f", self.tri_vertex),
        #      ("n3f", self.tri_normals),
        #      ("c3B", self.tri_color))
                    


class Arrow(Shape):
    def __init__(self, start, end, orientation=0.0, width=0.05, color=gray):
        self.start = start
        self.end = end
        self.orientation = orientation
        self.width = width
        self.color = color
        self.axis = end - start

        self.vertices = np.array([])
        self.normals = np.array([])

        self._generate_vertices()

    def _generate_vertices(self):
        length = distance(self.start, self.end)
        # Generate the arrow along z-axis and then rotate it

        #   ____|\
        #  |____  *
        #       |/

        
        # First the arrow rectangle
        width = self.width
        headl = width*2.0
        headw = width*2.0
        
        a = np.array([-width/2, 0.0, 0.0])
        b = np.array([+width/2, 0.0, 0.0])
        
        c = np.array([-width/2, 0.0, length - headl])
        d = np.array([+width/2, 0.0, length - headl])
        
        # Now the arrow head
        t1 = np.array([-headw/2, 0.0, length - headl])
        t2 = np.array([+headw/2, 0.0, length - headl])
        t3 = np.array([0.0, 0.0, length])
        
        self.vertices = np.array([a,b,c,d,t1,t2,t3])
        self.normals =  np.array([[0.0, 1.0, 0.0]]*len(self.vertices))

        # Orient it
        self.rotate([0.0, 0.0, 1.0], self.orientation)
        
        # Align with start-end direction
        ang = angle_between_vectors(np.array([0.0, 0.0, 1.0]), self.axis)
        
        normal = np.cross(self.axis, np.array([0.0, 0.0, 1.0]))
        self.rotate(normal, ang)
        self.translate(self.end)
        
    def draw(self):
        indexed = [0, 1, 2, 1, 2, 3, 4, 5, 6]
        
        triangles = len(indexed)
        draw(triangles, pyglet.gl.GL_TRIANGLES,
             ("v3f", self.vertices[indexed,].flatten()),
             ("n3f", self.normals[indexed,].flatten()),
             ("c3B", self.color*triangles))

    def rotate(self, axis, angle):
        # Check if zero
        #if np.allclose(axis, 0):
            # No rotation around a null axis
        #    return
        
        rotmat = rotation_matrix(angle, axis)[:3,:3]
        # Trick on stackoverflow to use the rotation matrix on a set of coordinates
        #for i, v in enumerate(self.vertices):
        #    self.vertices[i] = np.dot(rotmat, v)
        self.vertices = np.dot(self.vertices, rotmat.T)
            
