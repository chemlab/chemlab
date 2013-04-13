from .base import ShaderBaseRenderer
from ..buffers import VertexBuffer
import numpy as np
import pkgutil
from OpenGL.GL import *

class LineRenderer(ShaderBaseRenderer):
    '''Render a set of lines.
    
    .. image:: /_static/line_renderer.png
    
    **Parameters**
    
    widget:
        The parent QChemlabWidget
    startends: np.ndarray((NLINES, 2, 3), dtype=float)
        Start and end position of each line in the form of an array::

            s1 = [0.0, 0.0, 0.0]
            startends = [[s1, e1], [s2, e2], ..]
         
    colors: np.ndarray((NLINES, 2, 4), dtype=np.uint8)
        The corresponding color of each extrema of each line.
    
    '''
    def __init__(self, widget, startends, colors, width=1.5):
        vert = pkgutil.get_data("chemlab.graphics.renderers.shaders",
                                "default_persp.vert")
        frag = pkgutil.get_data("chemlab.graphics.renderers.shaders",
                                "no_light.frag")
        super(LineRenderer, self).__init__(widget, vert, frag)

        self.width = width
        self.viewer = widget
        self.n_lines = len(startends)
        
        vertices = np.array(startends, dtype=np.float32)
        colors = np.array(colors, dtype=np.uint8)
        
        self._vbo_v = VertexBuffer(vertices, GL_DYNAMIC_DRAW)
        self._vbo_c = VertexBuffer(colors, GL_DYNAMIC_DRAW)
        
    def draw_vertices(self):
        glLineWidth(self.width)
        glEnable(GL_LINE_SMOOTH)
        
        glEnableClientState(GL_VERTEX_ARRAY)
        self._vbo_v.bind_vertexes(3, GL_FLOAT)
        
        glEnableClientState(GL_COLOR_ARRAY)
        self._vbo_c.bind_colors(4, GL_UNSIGNED_BYTE)
        
        glDrawArrays(GL_LINES, 0, self.n_lines)
        
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        
        self._vbo_v.unbind()
        self._vbo_c.unbind()
        
        glLineWidth(1)
        glDisable(GL_LINE_SMOOTH)        
    def update_positions(self, vertices):
        """Update the line positions
        """

        vertices = np.array(vertices, dtype=np.float32)
        self._vbo_v.set_data(vertices)
        self._vbo_v.unbind()
        
    def update_colors(self, colors):
        """Update the colors"""
        
        colors = np.array(colors, dtype=np.uint8)
        self._vbo_c.set_data(colors)
        self._vbo_c.unbind()
        
