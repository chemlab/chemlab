from .base import ShaderBaseRenderer
import pkgutil

from ..shaders import set_uniform
from ..buffers import VertexBuffer
from OpenGL.GL import *
import numpy as np

class CylinderImpostorRenderer(ShaderBaseRenderer):
    """

    """
    def __init__(self, viewer, bounds, radii, colors):
        vert = pkgutil.get_data("chemlab.graphics.renderers.shaders",
                                              "cylinderimp.vert")
        frag = pkgutil.get_data("chemlab.graphics.renderers.shaders",
                                                "cylinderimp.frag")
        
        super(CylinderImpostorRenderer, self).__init__(viewer, vert, frag)
        # We need to do it first for 1 cylinder
        self.bounds = bounds
        self.radii = radii
        self.colors = colors
        self.n_cylinders = len(bounds)
        
        self.ldir = np.array([0.0, 0.0, 10.0, 1.0])

        # We pass the starting position 8 times, and each of these has
        # a mapping to the bounding box corner.
        vertices = np.repeat(bounds[:, 0], 36, axis=0).astype('float32')
        directions = np.repeat(bounds[:, 1] - bounds[:, 0],
                               36, axis=0).astype('float32')
        colors = np.repeat(colors, 36, axis=0).astype('uint8')
        radii = np.repeat(radii, 36, axis=0).astype('float32')
        
        local = np.array([
           # First face -- front
          0.0, 0.0, 0.0,
          0.0, 1.0, 0.0, 
          1.0, 1.0, 0.0,
        
          0.0, 0.0, 0.0,
          1.0, 1.0, 0.0,
          1.0, 0.0, 0.0,

          # Second face -- back
          0.0, 0.0, 1.0,
          0.0, 1.0, 1.0, 
          1.0, 1.0, 1.0,

          0.0, 0.0, 1.0,
          1.0, 1.0, 1.0,
          1.0, 0.0, 1.0,
          
          # Third face -- left
          0.0, 0.0, 0.0,
          0.0, 0.0, 1.0, 
          0.0, 1.0, 1.0,

          0.0, 0.0, 0.0,
          0.0, 1.0, 1.0,
          0.0, 1.0, 0.0,

          # Fourth face -- right
          1.0, 0.0, 0.0,
          1.0, 0.0, 1.0, 
          1.0, 1.0, 1.0,

          1.0, 0.0, 0.0,
          1.0, 1.0, 1.0,
          1.0, 1.0, 0.0,

          # Fifth face -- up
          0.0, 1.0, 0.0,
          0.0, 1.0, 1.0,
          1.0, 1.0, 1.0,

          0.0, 1.0, 0.0,
          1.0, 1.0, 1.0,
          1.0, 1.0, 0.0,
          
          # Sixth face -- down
          0.0, 0.0, 0.0,
          0.0, 0.0, 1.0,
          1.0, 0.0, 1.0,

          0.0, 0.0, 0.0,
          1.0, 0.0, 1.0,
          1.0, 0.0, 0.0,
          
        ]).astype('float32')
        
        local = np.tile(local, self.n_cylinders)
        
        self._verts_vbo = VertexBuffer(vertices,GL_DYNAMIC_DRAW)
        self._local_vbo = VertexBuffer(local,GL_DYNAMIC_DRAW)
        self._directions_vbo = VertexBuffer(directions, GL_DYNAMIC_DRAW)
        self._color_vbo = VertexBuffer(colors, GL_DYNAMIC_DRAW)
        self._radii_vbo = VertexBuffer(radii, GL_DYNAMIC_DRAW)

    def setup_shader(self):
        glUseProgram(self.shader)
        set_uniform(self.shader, 'model_view_rotation_mat', 'mat4fv',
                    self.viewer.camera._get_rotation_matrix())
        
        set_uniform(self.shader, 'model_view_mat', 'mat4fv',
                    self.viewer.camera.matrix)
        
        set_uniform(self.shader, 'model_view_projection_mat', 'mat4fv',
                    np.dot(self.viewer.camera.projection,
                           self.viewer.camera.matrix))
        
        set_uniform(self.shader, 'projection_mat', 'mat4fv',
                    self.viewer.camera.projection)
        
        #set_uniform(self.shader, 'light_dir', '3f', self.ldir[:3])
        
        cam = np.dot(self.viewer.camera.matrix[:3,:3],
                     -self.viewer.camera.position)
        
        set_uniform(self.shader, 'camera', '4f', cam)
        
    def draw(self):
        self.setup_shader()
        
        local_attr = glGetAttribLocation(self.shader,
                                         "vert_local_coordinate")
        cylinder_axis_attr = glGetAttribLocation(self.shader,
                                               "cylinder_axis")

        radius_attr = glGetAttribLocation(self.shader,
                                          "cylinder_radius")

        glEnableVertexAttribArray(local_attr)        
        glEnableVertexAttribArray(cylinder_axis_attr)
        glEnableVertexAttribArray(radius_attr)        
        
        glEnableClientState(GL_VERTEX_ARRAY)
        self._verts_vbo.bind_vertexes(3, GL_FLOAT)
        
        self._local_vbo.bind_attrib(local_attr, 3, GL_FLOAT)
        self._directions_vbo.bind_attrib(cylinder_axis_attr, 3, GL_FLOAT)
        self._radii_vbo.bind_attrib(radius_attr, 1, GL_FLOAT)

        glEnableClientState(GL_COLOR_ARRAY)
        self._color_vbo.bind_colors(4, GL_UNSIGNED_BYTE)
        
        glDrawArrays(GL_TRIANGLES, 0, 3 * 36 * self.n_cylinders)
        
        self._verts_vbo.unbind()
        self._local_vbo.unbind()
        self._color_vbo.unbind()
        self._radii_vbo.unbind()
        self._directions_vbo.unbind()
        
        glDisableVertexAttribArray(local_attr)        
        glDisableVertexAttribArray(cylinder_axis_attr)
        glDisableVertexAttribArray(radius_attr)

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        glUseProgram(0)
        
    def update_positions(self, rarray):
        vertices = np.repeat(rarray, 4, axis=0).astype(np.float32)
        self.poslist = rarray
        
        self._verts_vbo.set_data(vertices)
        self._centers_vbo.set_data(vertices)
        
