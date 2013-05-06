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
                                                "no_light.frag")
        
        super(CylinderImpostorRenderer, self).__init__(viewer, vert, frag)
        
        self.bounds = bounds
        self.radii = radii
        self.colors = colors
        self.n_cylinders = len(bounds)
        
        self.ldir = np.array([0.0, 0.0, 10.0, 1.0])
        
        vertices = np.repeat(bounds, 2, axis=1).astype(np.float32)
        radii = np.repeat(radii, 4, axis=0).astype(np.float32)
        colors = np.repeat(colors, 4, axis=0).astype(np.uint8)
        directions = np.repeat(bounds[:, 1] - bounds[:, 0], 4, axis=0).astype(np.float32)

        mapping = np.tile([-1, -1, # Black corner
                           1, -1, # Red Corner
                           1, 1,  # Yellow corner
                           -1, 1],
                          self.n_cylinders).astype(np.float32)
        
        self._verts_vbo = VertexBuffer(vertices,GL_DYNAMIC_DRAW)
        self._color_vbo = VertexBuffer(colors,GL_DYNAMIC_DRAW)
        self._mapping_vbo = VertexBuffer(mapping,GL_DYNAMIC_DRAW)
        #self._centers_vbo = VertexBuffer(vertices,GL_DYNAMIC_DRAW)
        self._radii_vbo = VertexBuffer(radii,GL_DYNAMIC_DRAW)
        self._directions_vbo = VertexBuffer(directions, GL_DYNAMIC_DRAW)
        

    def setup_shader(self):
        glUseProgram(self.shader)
        set_uniform(self.shader, 'camera_mat', 'mat4fv',
                    self.viewer.camera.matrix)
        
        set_uniform(self.shader, 'camera_rotation', 'mat4fv',
                    self.viewer.camera._get_rotation_matrix())
        
        set_uniform(self.shader, 'projection_mat', 'mat4fv',
                    self.viewer.camera.projection)
        
        set_uniform(self.shader, 'mvproj', 'mat4fv',
                    np.dot(self.viewer.camera.projection, self.viewer.camera.matrix))
        
        set_uniform(self.shader, 'light_dir', '3f', self.ldir[:3])
        
        #set_uniform(self.shader, 'scalefac', '1f', 1.5)
        
        cam = np.dot(self.viewer.camera.matrix[:3,:3],
                     -self.viewer.camera.position)
        
        set_uniform(self.shader, 'camera', '4f', cam)
        
    def draw(self):
        self.setup_shader()
        
        at_mapping = glGetAttribLocation(self.shader,
                                         "at_mapping")
        #at_cylinder_direction = glGetAttribLocation(self.shader,
        #                                       "at_cylinder_direction")
        
        glEnableVertexAttribArray(at_mapping)        
        #glEnableVertexAttribArray(at_cylinder_direction)
        
        glEnableClientState(GL_VERTEX_ARRAY)
        self._verts_vbo.bind_vertexes(3, GL_FLOAT)
        
        self._mapping_vbo.bind_attrib(at_mapping, 2, GL_FLOAT)
        #self._directions_vbo.bind_attrib(at_cylinder_direction, 3, GL_FLOAT)
        #self._radii_vbo.bind_attrib(at_cylinder_radius, 1, GL_FLOAT)

        glEnableClientState(GL_COLOR_ARRAY)
        self._color_vbo.bind_colors(4, GL_UNSIGNED_BYTE)
        
        glDrawArrays(GL_QUADS, 0, 4*self.n_cylinders)
        
        self._verts_vbo.unbind()
        self._mapping_vbo.unbind()
        self._directions_vbo.unbind()
        self._color_vbo.unbind()
        
        glDisableVertexAttribArray(at_mapping)        
        #glDisableVertexAttribArray(at_cylinder_direction)

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        glUseProgram(0)
        
    def update_positions(self, rarray):
        vertices = np.repeat(rarray, 4, axis=0).astype(np.float32)
        self.poslist = rarray
        
        self._verts_vbo.set_data(vertices)
        self._centers_vbo.set_data(vertices)
        
