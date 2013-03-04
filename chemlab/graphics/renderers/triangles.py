'''TriangleRenderer is the basics for other shapes, we pass just
triangle vertices and we got the result.

'''
import numpy as np

from .base import DefaultRenderer
from ..buffers import VertexBuffer

from OpenGL.GL import (GL_DYNAMIC_DRAW, GL_VERTEX_ARRAY, GL_NORMAL_ARRAY,
                       GL_COLOR_ARRAY, GL_UNSIGNED_BYTE, GL_FLOAT, GL_TRIANGLES,
                       glEnableClientState, glDrawArrays)

class TriangleRenderer(DefaultRenderer):
    def __init__(self, viewer, vertices, normals, colors):
        super(TriangleRenderer, self).__init__(viewer)
        
        n_triangles = len(vertices)
        # Convert arrays to numpy arrays, float32 precision,
        # compatible with opengl, and cast to ctypes
        vertices = np.array(vertices, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        colors = np.array(colors, dtype=np.uint8)
        
        # Store vertices, colors and normals in 3 different vertex
        # buffer objects
        self._vbo_v = VertexBuffer(vertices, GL_DYNAMIC_DRAW)
        self._vbo_n = VertexBuffer(normals, GL_DYNAMIC_DRAW)
        self._vbo_c = VertexBuffer(colors, GL_DYNAMIC_DRAW)
        
        self._n_triangles = n_triangles

    def draw_vertices(self):
        # Draw all the vbo defined in set_atoms
        glEnableClientState(GL_VERTEX_ARRAY)
        self._vbo_v.bind_vertexes(3, GL_FLOAT)
        
        glEnableClientState(GL_NORMAL_ARRAY)
        self._vbo_n.bind_normals(GL_FLOAT)
        
        glEnableClientState(GL_COLOR_ARRAY)
        self._vbo_c.bind_colors(4, GL_UNSIGNED_BYTE)
        
        glDrawArrays(GL_TRIANGLES, 0, self._n_triangles)
    
    def update_vertices(self, vertices):
        vertices = np.array(vertices, dtype=np.float32)
        self._vbo_v.set_data(vertices)
        
    def update_normals(self, normals):
        normals = np.array(normals, dtype=np.float32)
        self._vbo_n.set_data(normals)

    def update_colors(self, colors):
        colors = np.array(colors, dtype=np.float32)
        self._vbo_c.set_data(colors)

