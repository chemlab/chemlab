from .base import ShaderBaseRenderer
from ..buffers import VertexBuffer
import numpy as np
import pkgutil
from OpenGL.GL import *

class LineRenderer(ShaderBaseRenderer):
    def __init__(self, viewer, startends, colors):
        vert = pkgutil.get_data("chemlab.graphics.renderers.shaders",
                                "default_persp.vert")
        frag = pkgutil.get_data("chemlab.graphics.renderers.shaders",
                                "no_light.frag")
        super(LineRenderer, self).__init__(viewer, vert, frag)

        self.viewer = viewer
        self.n_lines = len(startends)
        
        vertices = np.array(startends, dtype=np.float32)
        colors = np.array(colors, dtype=np.uint8)
        
        self._vbo_v = VertexBuffer(vertices, GL_DYNAMIC_DRAW)
        self._vbo_c = VertexBuffer(colors, GL_DYNAMIC_DRAW)
        
    def draw_vertices(self):
        glEnableClientState(GL_VERTEX_ARRAY)
        self._vbo_v.bind_vertexes(3, GL_FLOAT)
        
        glEnableClientState(GL_COLOR_ARRAY)
        self._vbo_c.bind_colors(4, GL_UNSIGNED_BYTE)
        
        glDrawArrays(GL_LINES, 0, self.n_lines)
        
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        
        self._vbo_v.unbind()
        self._vbo_c.unbind()
        
    def update_positions(self, vertices):
        vertices = np.array(vertices, dtype=np.float32)
        self._vbo_v.set_data(vertices)
        self._vbo_v.unbind()
        
    def update_colors(self, colors):
        colors = np.array(colors, dtype=np.float32)
        self._vbo_c.set_data(colors)
        self._vbo_c.unbind()
        
