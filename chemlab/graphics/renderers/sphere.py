import numpy as np

from pyglet.gl import *
from pyglet.graphics.vertexbuffer import VertexBufferObject
from .base import AbstractRenderer
from .triangles import TriangleRenderer
from ..optshapes import OptSphere


class SphereRenderer(AbstractRenderer):
    def __init__(self, poslist, radiuslist, colorlist):
        '''Renders a set of spheres. The positions of the spheres
        are determined from *poslist* which is a list of xyz coordinates,
        the respective radii are in the list *radiuslist* and colors
        *colorlist* as rgba where each one is in the range [0, 255].

        This renderer uses vertex array objects to deliver optimal
        performance.
        '''
        

        self.poslist = poslist
        self.radiuslist = radiuslist
        self.colorlist = colorlist
        self.n_spheres = len(poslist)
        
        # We expect to receive things in nanometers
        vertices = []
        normals = []
        colors_ = []
        
        for coords, radius, color in zip(poslist, radiuslist, colorlist):
            s = OptSphere(radius, coords, color=color)
            vertices.append(s.tri_vertex)
            normals.append(s.tri_normals)
            colors_.append(s.tri_color)
        
        vertices = np.array(vertices)
        vertices = vertices.reshape((s.tri_n * self.n_spheres, 3))
        
        self.tr = TriangleRenderer(vertices, normals, colors_)
    
    def draw(self):
        self.tr.draw()

    def update_positions(self, rarray):
        offset = 0
        vertices = np.zeros(self._n_triangles*3, dtype=np.float32)
        
        for i in range(len(rarray)):
            color = self.colorlist[i]
            radius = self.radiuslist[i]
            s = OptSphere(radius, rarray[i], color=color)
            
            n = len(s.tri_vertex)
            vertices[offset:offset+n] = s.tri_vertex
            offset += n
        
        self.tr.update_vertices(vertices)
        self.poslist = rarray
        
    def update_colors(self, colorlist):
        self.colorlist = colorlist
        
        colors_ = []
        for coords, radius, color in zip(self.poslist, self.radiuslist, colorlist):
            s = OptSphere(radius, coords, color=color)
            colors_.append(s.tri_color)
        
        self.tr.update_colors(colors_)

class SphereRenderer2(AbstractRenderer):
    def __init__(self, poslist, radiuslist, colorlist):
        '''Renders a set of spheres. The positions of the spheres
        are determined from *poslist* which is a list of xyz coordinates,
        the respective radii are in the list *radiuslist* and colors
        *colorlist* as rgba where each one is in the range [0, 255].

        This renderer uses vertex array objects to deliver optimal
        performance.
        '''
        
        self.poslist = poslist
        self.radiuslist = radiuslist
        self.colorlist = colorlist
        
        # We expect to receive things in nanometers
        n_triangles = 0
        vertices = []
        normals = []
        colors_ = []
        
        for coords, radius, color in zip(poslist, radiuslist, colorlist):
            s = OptSphere(radius, coords, color=color)
            n_triangles += s.tri_n
            
            vertices.append(s.tri_vertex)
            normals.append(s.tri_normals)
            colors_.append(s.tri_color)
        
        # Convert arrays to numpy arrays, float32 precision,
        # compatible with opengl, and cast to ctypes
        vertices = np.array(vertices, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        colors_ = np.array(colors_, dtype=np.uint8)

        # Store vertices, colors and normals in 3 different vertex
        # buffer objects
        self._vbo_v = VertexBufferObject(n_triangles*3*sizeof(GLfloat),
                                         GL_ARRAY_BUFFER,
                                         GL_DYNAMIC_DRAW)
        self._vbo_v.bind()
        self._vbo_v.set_data(vertices.ctypes.data_as(POINTER(GLfloat)))
        self._vbo_v.unbind()
        
        self._vbo_n = VertexBufferObject(n_triangles*3*sizeof(GLfloat),
                                         GL_ARRAY_BUFFER,
                                         GL_DYNAMIC_DRAW)
        self._vbo_n.bind()
        self._vbo_n.set_data(normals.ctypes.data_as(POINTER(GLfloat)))
        self._vbo_n.unbind()

        self._vbo_c= VertexBufferObject(n_triangles*4*sizeof(GLubyte),
                                        GL_ARRAY_BUFFER,
                                        GL_DYNAMIC_DRAW)
        self._vbo_c.bind()
        self._vbo_c.set_data(colors_.ctypes.data_as(POINTER(GLuint)))
        self._vbo_c.unbind()
        
        self._n_triangles = n_triangles
    
    def draw(self):
        # Draw all the vbo defined in set_atoms
        glEnableClientState(GL_VERTEX_ARRAY)
        self._vbo_v.bind()
        glVertexPointer(3, GL_FLOAT, 0, 0)
        
        glEnableClientState(GL_NORMAL_ARRAY)
        self._vbo_n.bind()
        glNormalPointer(GL_FLOAT, 0, 0)
        
        glEnableClientState(GL_COLOR_ARRAY)
        self._vbo_c.bind()
        glColorPointer(4, GL_UNSIGNED_BYTE, 0, 0)
        
        glDrawArrays(GL_TRIANGLES, 0, self._n_triangles)
        
        self._vbo_v.unbind()
        self._vbo_n.unbind()
        self._vbo_c.unbind()
        
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)

    def update_positions(self, rarray):
        offset = 0
        vertices = np.zeros(self._n_triangles*3, dtype=np.float32)
        
        for i in range(len(rarray)):
            color = self.colorlist[i]
            radius = self.radiuslist[i]
            s = OptSphere(radius, rarray[i], color=color)
            
            n = len(s.tri_vertex)
            vertices[offset:offset+n] = s.tri_vertex
            offset += n
        
        self._vbo_v.bind()
        self._vbo_v.set_data(vertices.ctypes.data_as(POINTER(GLfloat)))
        self._vbo_v.unbind()
        
        self.poslist = rarray
        
    def update_colors(self, colorlist):
        self.colorlist = colorlist
        
        colors_ = []
        for coords, radius, color in zip(self.poslist, self.radiuslist, colorlist):
            s = OptSphere(radius, coords, color=color)
            colors_.append(s.tri_color)
        
        colors_ = np.array(colors_, dtype=np.uint8)
        
        self._vbo_c.bind()
        self._vbo_c.set_data(colors_.ctypes.data_as(POINTER(GLuint)))
        self._vbo_v.unbind()
