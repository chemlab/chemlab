from OpenGL.GL import (shaders,
                       GL_VERTEX_SHADER, GL_FRAGMENT_SHADER,
                       glUseProgram, GL_FALSE, GLfloat, GL_TRUE)
from ctypes import POINTER

from ..shaders import set_uniform, compileShader
import numpy as np
import pkgutil




class AbstractRenderer(object):
    '''AbstractRenderer is the standard interface for renderers. Each
    renderer have to implement an initialization function __init__ and
    a draw method to do the actual drawing using OpenGL or by using
    other, more basic, renderers.
    
    Usually the renderers have also some custom functions that they
    use to update themselves.  For example a SphereRenderer implements
    the function update_positions to move the spheres around without
    having to regenerate all of the other properties.

    .. seealso:: :doc:`/graphics` for a tutorial on how to develop a simple
                 renderer.
    
    **Parameters**
    
    widget: :py:class:`chemlab.graphics.QChemlabWidget`
         The parent `QChemlabWidget`. Renderers can use the widget
         to access the camera, lights, and other informations.
    
    args, kwargs: Any other argument that they may use.

    '''
    def __init__(self, widget, *args, **kwargs):
        pass
    
    def draw(self):
        '''Generic drawing function to be implemented by the
        subclasses.

        '''
        pass
    
    

class ShaderBaseRenderer(AbstractRenderer):
    '''
    Instruments OpenGL with a vertex and a fragment shader.
    
    This renderer automatically binds light and camera
    information. Subclasses should not reimplement the ``draw`` method
    but the ``draw_vertices`` method where you can bind and draw the
    objects.

    **Parameters**
    
    widget:
        The parent :py:class:`~chemlab.graphics.QChemlabWidget`
    vertex: str
        Vertex program as a string
    fragment: str
        Fragment program as a string
    
    '''
    def __init__(self, widget, vertex, fragment):
        self.viewer = widget
        self.VERTEX_SHADER = vertex
        self.FRAGMENT_SHADER = fragment
        self.compile_shader()
        
    def draw(self):
        self.setup_shader()
        self.draw_vertices()
        glUseProgram(0)
        
    def draw_vertices(self):
        '''Method to be reimplemented by the subclasses.

        '''
        raise NotImplementedError()
        
    def compile_shader(self):
        vertex = compileShader(self.VERTEX_SHADER,
                               GL_VERTEX_SHADER)
        fragment = compileShader(self.FRAGMENT_SHADER,
                                 GL_FRAGMENT_SHADER)
        
        self.shader = shaders.compileProgram(vertex, fragment)
        
    def setup_shader(self):
        glUseProgram(self.shader)
        # Setup the uniforms
        set_uniform(self.shader, "mvproj", "mat4fv", self.viewer.mvproj)
        set_uniform(self.shader, "lightDir", "3f", self.viewer.ldir)
        set_uniform(self.shader, "camera", "3f", self.viewer.camera.position)

class DefaultRenderer(ShaderBaseRenderer):
    '''Same as
    :py:class:`~chemlab.graphics.renderers.ShaderBaseRenderer` with
    the default shaders.

    You can find the shaders in ``chemlab/graphics/renderers/shaders/``
    under the names of ``default_persp.vert`` and ``default_persp.frag``.

    '''
    
    def __init__(self, widget):
        vert = pkgutil.get_data("chemlab.graphics.renderers.shaders",
                                              "default_persp.vert")
        frag = pkgutil.get_data("chemlab.graphics.renderers.shaders",
                                                "default_light.frag")
        
        super(DefaultRenderer, self).__init__(widget, vert, frag)

        
    def setup_shader(self):
        super(DefaultRenderer, self).setup_shader()
        set_uniform(self.shader, "viewmatrix", "mat4fv",
                    self.viewer.camera._get_rotation_matrix().transpose())        
    
    def draw_vertices(self):
        '''Subclasses should reimplement this method.

        '''
        raise NotImplementedError()