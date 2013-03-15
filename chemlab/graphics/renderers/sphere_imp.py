from .base import ShaderBaseRenderer
import pkgutil

from ..shaders import set_uniform
from ..buffers import VertexBuffer
from OpenGL.GL import *
import numpy as np

class SphereImpostorRenderer(ShaderBaseRenderer):
    def __init__(self, viewer, poslist, radiuslist, colorlist):
        vert = pkgutil.get_data("chemlab.graphics.renderers.shaders",
                                              "sphereimp.vert")
        frag = pkgutil.get_data("chemlab.graphics.renderers.shaders",
                                                "sphereimp.frag")
        
        super(SphereImpostorRenderer, self).__init__(viewer, vert, frag)
        
        self.poslist = poslist
        self.radiuslist = radiuslist
        self.colorlist = colorlist
        self.n_spheres = len(poslist)
        self.ldir = np.array([0.0, 10.0, 10.0, 1.0])
        
        vertices = np.repeat(poslist, 4, axis=0).astype(np.float32)
        radii = np.repeat(radiuslist, 4, axis=0).astype(np.float32)
        colors = np.repeat(colorlist, 4, axis=0).astype(np.uint8)
        
        mapping = np.tile([1.0, 1.0,-1.0, 1.0,-1.0,-1.0,1.0, -1.0,],
                          self.n_spheres).astype(np.float32)
        
        self._verts_vbo = VertexBuffer(vertices,GL_DYNAMIC_DRAW)
        self._color_vbo = VertexBuffer(colors,GL_DYNAMIC_DRAW)
        self._mapping_vbo = VertexBuffer(mapping,GL_DYNAMIC_DRAW)
        self._centers_vbo = VertexBuffer(vertices,GL_DYNAMIC_DRAW)
        self._radius_vbo = VertexBuffer(radii,GL_DYNAMIC_DRAW)

    def setup_shader(self):
        glUseProgram(self.shader)
        set_uniform(self.shader, 'camera_mat', 'mat4fv',
                    self.viewer.camera.matrix)
        
        
        set_uniform(self.shader, 'projection_mat', 'mat4fv',
                    self.viewer.camera.projection)
        set_uniform(self.shader, 'mvproj', 'mat4fv',
                    self.viewer.camera.projection)
        
        set_uniform(self.shader, 'light_dir', '3f', self.ldir[:3])
        
        set_uniform(self.shader, 'scalefac', '1f', 1.5)
        cam = np.dot(self.viewer.camera.matrix[:3,:3],
                     -self.viewer.camera.position)
        set_uniform(self.shader, 'camera', '4f', cam)
        
    def draw(self):
        self.setup_shader()
        
        at_mapping = glGetAttribLocation(self.shader,
                                         "at_mapping")
        at_sphere_center = glGetAttribLocation(self.shader,
                                               "at_sphere_center")
        at_sphere_radius = glGetAttribLocation(self.shader,
                                               "at_sphere_radius")
        
        glEnableVertexAttribArray(at_mapping)        
        glEnableVertexAttribArray(at_sphere_center)
        glEnableVertexAttribArray(at_sphere_radius)
        
        glEnableClientState(GL_VERTEX_ARRAY)
        self._verts_vbo.bind_vertexes(3, GL_FLOAT)
        
        self._mapping_vbo.bind_attrib(at_mapping, 2, GL_FLOAT)
        self._centers_vbo.bind_attrib(at_sphere_center, 3, GL_FLOAT)
        self._radius_vbo.bind_attrib(at_sphere_radius, 1, GL_FLOAT)

        glEnableClientState(GL_COLOR_ARRAY)
        self._color_vbo.bind_colors(4, GL_UNSIGNED_BYTE)
        
        glDrawArrays(GL_QUADS, 0, 4*self.n_spheres)
        
        self._mapping_vbo.unbind()
        self._centers_vbo.unbind()
        self._radius_vbo.unbind()
        
    def update_positions(self, rarray):
        vertices = np.repeat(rarray, 4, axis=0).astype(np.float32)
        self.poslist = rarray
        
        self._verts_vbo.set_data(vertices)
        self._centers_vbo.set_data(vertices)