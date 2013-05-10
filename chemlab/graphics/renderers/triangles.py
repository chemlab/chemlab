'''TriangleRenderer is the basics for other shapes, we pass just
triangle vertices and we got the result.

'''
import numpy as np

from .base import DefaultRenderer
from ..buffers import VertexBuffer
from ..shaders import set_uniform

from OpenGL.GL import (GL_DYNAMIC_DRAW, GL_VERTEX_ARRAY, GL_NORMAL_ARRAY,
                       GL_COLOR_ARRAY, GL_UNSIGNED_BYTE, GL_FLOAT, GL_TRIANGLES,
                       glEnableClientState, glDrawArrays)

class TriangleRenderer(DefaultRenderer):
    '''Renders an array of triangles.

    A lot of renderers are built on this, for example
    :py:class:`~chemlab.graphics.renderers.SphereRenderer`. The
    implementation is relatively fast since it's based on
    VertexBuffers.
    
    .. image:: /_static/triangle_renderer.png
    
    **Parameters**
    
    widget:
        The parent QChemlabWidget
    vertices: np.ndarray((NTRIANGLES*3, 3), dtype=float)
        The triangle vertices, keeping in mind the unwinding order.
        If the face of the triangle is pointing outwards, the vertices should
        be provided in clokckwise order.
    normals: np.ndarray((NTRIANGLES*3, 3), dtype=float)
        The normals to each of the triangle vertices, used for
        lighting calculations.
    colors: np.ndarray((NTRIANGLES*3, 4), dtype=np.uint8)
        Color for each of the vertices in (r,g,b,a) values
        in the interval [0, 255]
    
    '''
    def __init__(self, widget, vertices, normals, colors, shading='phong'):
        super(TriangleRenderer, self).__init__(widget)
        
        n_triangles = len(vertices)
        # Convert arrays to numpy arrays, float32 precision,
        # compatible with opengl, and cast to ctypes
        vertices = np.array(vertices, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        colors = np.array(colors, dtype=np.uint8)
        
        self.shading = shading
        
        # Store vertices, colors and normals in 3 different vertex
        # buffer objects
        self._vbo_v = VertexBuffer(vertices, GL_DYNAMIC_DRAW)
        self._vbo_n = VertexBuffer(normals, GL_DYNAMIC_DRAW)
        self._vbo_c = VertexBuffer(colors, GL_DYNAMIC_DRAW)
        
        self._n_triangles = n_triangles
        
    def setup_shader(self):
        super(TriangleRenderer, self).setup_shader()
        
        shd = {'phong' : 0,
               'toon': 1}[self.shading]
        
        set_uniform(self.shader, 'shading_type', '1i', shd)
        
    def draw_vertices(self):
        # Draw all the vbo defined in set_atoms
        glEnableClientState(GL_VERTEX_ARRAY)
        self._vbo_v.bind_vertexes(3, GL_FLOAT)
        
        glEnableClientState(GL_NORMAL_ARRAY)
        self._vbo_n.bind_normals(GL_FLOAT)
        
        glEnableClientState(GL_COLOR_ARRAY)
        self._vbo_c.bind_colors(4, GL_UNSIGNED_BYTE)
        
        glDrawArrays(GL_TRIANGLES, 0, self._n_triangles)
        
        self._vbo_v.unbind()
        self._vbo_n.unbind()
        self._vbo_c.unbind()
    
    def update_vertices(self, vertices):
        """
        Update the triangle vertices.
        """

        vertices = np.array(vertices, dtype=np.float32)
        self._vbo_v.set_data(vertices)
        
    def update_normals(self, normals):
        """
        Update the triangle normals.
        """

        normals = np.array(normals, dtype=np.float32)
        self._vbo_n.set_data(normals)

    def update_colors(self, colors):
        '''
        Update the triangle colors.
        '''
        colors = np.array(colors, dtype=np.float32)
        self._vbo_c.set_data(colors)

