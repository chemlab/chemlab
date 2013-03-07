from .base import ShaderBaseRenderer
from OpenGL.GL import *
from ..buffers import VertexBuffer

import numpy as np
import pkgutil

class PointRenderer(ShaderBaseRenderer):
    
    def __init__(self, viewer, positions, colors):
        vert = pkgutil.get_data("chemlab.graphics.renderers.shaders",
                                "default_persp.vert")
        frag = pkgutil.get_data("chemlab.graphics.renderers.shaders",
                                "no_light.frag")
        super(PointRenderer, self).__init__(viewer, vert, frag)

        glPointSize(2.0)
        glEnable(GL_POINT_SMOOTH)        
        
        self.viewer = viewer
        self.n_points = len(positions)
        
        vertices = np.array(positions, dtype=np.float32)
        colors = np.array(colors, dtype=np.uint8)
        
        self._vbo_v = VertexBuffer(vertices, GL_DYNAMIC_DRAW)
        self._vbo_c = VertexBuffer(colors, GL_DYNAMIC_DRAW)
        
    def draw_vertices(self):
        glEnableClientState(GL_VERTEX_ARRAY)
        self._vbo_v.bind_vertexes(3, GL_FLOAT)
        
        glEnableClientState(GL_COLOR_ARRAY)
        self._vbo_c.bind_colors(4, GL_UNSIGNED_BYTE)
        
        glDrawArrays(GL_POINTS, 0, self.n_points)
        
        
    def update_positions(self, vertices):
        vertices = np.array(vertices, dtype=np.float32)
        self._vbo_v.set_data(vertices)
        
    def update_colors(self, colors):
        colors = np.array(colors, dtype=np.float32)
        self._vbo_c.set_data(colors)

