'''TriangleRenderer is the basics for other shapes, we pass just
triangle vertices and we got the result.

'''
import numpy as np

from .base import AbstractRenderer
from pyglet.graphics.vertexbuffer import VertexBufferObject
from pyglet.gl import *


class TriangleRenderer(AbstractRenderer):
    def __init__(self, vertices, normals, colors):
        n_triangles = len(vertices)
        # Convert arrays to numpy arrays, float32 precision,
        # compatible with opengl, and cast to ctypes
        vertices = np.array(vertices, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        colors = np.array(colors, dtype=np.uint8)
        
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
        self._vbo_c.set_data(colors.ctypes.data_as(POINTER(GLuint)))
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
    
    def update_vertices(self, vertices):
        vertices = np.array(vertices, dtype=np.float32)
        self._vbo_v.bind()
        self._vbo_v.set_data(vertices.ctypes.data_as(POINTER(GLfloat)))
        self._vbo_v.unbind()
        
    def update_normals(self, normals):
        normals = np.array(vertices, dtype=np.float32)
        self._vbo_n.bind()
        self._vbo_n.set_data(normals.ctypes.data_as(POINTER(GLfloat)))
        self._vbo_n.unbind()

    def update_colors(self, colors):
        colors = np.array(colors, dtype=np.float32)
        self._vbo_c.bind()
        self._vbo_c.set_data(colors.ctypes.data_as(POINTER(GLuint)))
        self._vbo_c.unbind()
