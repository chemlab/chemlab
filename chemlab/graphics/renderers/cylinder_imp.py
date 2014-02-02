from .base import ShaderBaseRenderer
import pkgutil

from ..shaders import set_uniform
from ..buffers import VertexBuffer
from OpenGL.GL import *
import numpy as np

class CylinderImpostorRenderer(ShaderBaseRenderer):
    """Render pixel-perfect cylinders by using raytraced impostors.
    
    This method provide a very fast way to render cylinders by using
    an advanced shader program. It should be the preferred way to
    render cylinders.

    """
    
    def __init__(self, widget, bounds, radii, colors, shading='phong'):
        vert = pkgutil.get_data("chemlab.graphics.renderers.shaders",
                                              "cylinderimp.vert")
        frag = pkgutil.get_data("chemlab.graphics.renderers.shaders",
                                                "cylinderimp.frag")
        
        super(CylinderImpostorRenderer, self).__init__(widget, vert, frag)
        self.shading = shading
        self.ldir = np.array([0.0, 0.0, 10.0, 1.0])
        self.widget = widget

        self.change_attributes(bounds, radii, colors)
        self.widget.update()

    def change_attributes(self, bounds, radii, colors):
        """Reinitialize the buffers, to accomodate the new
        attributes. This is used to change the number of cylinders to
        be displayed.

        """
        
        self.n_cylinders = len(bounds)
        self.is_empty = True if self.n_cylinders == 0 else False
        
        if self.is_empty:
            self.bounds = bounds
            self.radii = radii
            self.colors = colors
            return # Do nothing
        
        # We pass the starting position 8 times, and each of these has
        # a mapping to the bounding box corner.
        self.bounds = np.array(bounds, dtype='float32')
        vertices, directions = self._gen_bounds(self.bounds) 
        
        self.radii = np.array(radii, dtype='float32')
        prim_radii = self._gen_radii(self.radii)

        self.colors = np.array(colors, dtype='uint8')
        prim_colors = self._gen_colors(self.colors)
       
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
        self._directions_vbo = VertexBuffer(directions, GL_DYNAMIC_DRAW)
        
        self._local_vbo = VertexBuffer(local,GL_DYNAMIC_DRAW)
        self._color_vbo = VertexBuffer(prim_colors, GL_DYNAMIC_DRAW)
        self._radii_vbo = VertexBuffer(prim_radii, GL_DYNAMIC_DRAW)

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
        
        set_uniform(self.shader, 'light_dir', '3f', self.ldir[:3])

        
        cam = np.dot(self.viewer.camera.matrix[:3,:3],
                     -self.viewer.camera.position)
        set_uniform(self.shader, 'camera_position', '3f', cam)
        
        shd = {'phong' : 0,
               'toon': 1}[self.shading]
        
        set_uniform(self.shader, 'shading_type', '1i', shd)
        
    def draw(self):
        if self.is_empty:
            return # Do nothing

        self.setup_shader()
        
        local_attr = glGetAttribLocation(self.shader,
                                         b"vert_local_coordinate")
        cylinder_axis_attr = glGetAttribLocation(self.shader,
                                               b"cylinder_axis")

        radius_attr = glGetAttribLocation(self.shader,
                                          b"cylinder_radius")

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
        
        glDrawArrays(GL_TRIANGLES, 0, 36 * self.n_cylinders)
        
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

        
    def _gen_bounds(self, bounds):
        vertices = np.repeat(bounds[:, 0], 36, axis=0).astype('float32')
        directions = np.repeat(bounds[:, 1] - bounds[:, 0],
                               36, axis=0).astype('float32')
        return vertices, directions
        
    def _gen_radii(self, radii):
        return np.repeat(radii, 36, axis=0).astype('float32')
        
    def _gen_colors(self, colors):
        return np.repeat(colors, 36, axis=0).astype('uint8')
        
    def update_bounds(self, bounds):
        '''Update the bounds inplace'''
        self.bounds = np.array(bounds, dtype='float32')
        vertices, directions = self._gen_bounds(self.bounds) 
        
        self._verts_vbo.set_data(vertices)
        self._directions_vbo.set_data(directions)
        self.widget.update()
        
    def update_radii(self, radii):
        '''Update the radii inplace'''
        self.radii = np.array(radii, dtype='float32')
        prim_radii = self._gen_radii(self.radii)
        
        self._radii_vbo.set_data(prim_radii)
        self.widget.update()

    def update_colors(self, colors):
        '''Update the colors inplace'''
        self.colors = np.array(colors, dtype='uint8')
        prim_colors = self._gen_colors(self.colors)
        
        self._color_vbo.set_data(prim_colors)
        self.widget.update()
