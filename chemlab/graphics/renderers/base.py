from OpenGL.GL import (shaders,
                       GL_VERTEX_SHADER, GL_FRAGMENT_SHADER,
                       glUseProgram, GL_FALSE, GLfloat, GL_TRUE)
from ctypes import POINTER

from ..shaders import set_uniform
import numpy as np
import pkgutil


class AbstractRenderer(object):
    '''An AbstractRenderer is an interface for Renderers. Each
    renderer have to implement an initialization function __init__, a
    draw method to do the actual drawing and an update function, that
    is used to update the data to be displayed.

    '''
    def __init__(self, viewer, *args, **kwargs):
        pass
    
    def draw(self):
        pass
    
    def update(self, *args, **kwargs):
        pass
    

class ShaderBaseRenderer(AbstractRenderer):
    def __init__(self, widget, vertex, fragment):
        self.viewer = widget
        self.VERTEX_SHADER = vertex
        self.FRAGMENT_SHADER = fragment
        self.compile_shader()
        
    def draw(self):
        self.setup_shader()
        self.draw_vertices()
        
    def draw_vertices(self):
        raise NotImplementedError()
        
    def compile_shader(self):
        vertex = shaders.compileShader(self.VERTEX_SHADER,
                                       GL_VERTEX_SHADER)
        fragment = shaders.compileShader(self.FRAGMENT_SHADER,
                                         GL_FRAGMENT_SHADER)
        
        self.shader = shaders.compileProgram(vertex, fragment)
        
    def setup_shader(self):
        glUseProgram(self.shader)
        # Setup the uniforms
        set_uniform(self.shader, "mvproj", "mat4fv", self.viewer.mvproj)
        set_uniform(self.shader, "lightDir", "3f", self.viewer.ldir)
        set_uniform(self.shader, "camera", "3f", self.viewer.camera.position)

class DefaultRenderer(ShaderBaseRenderer):
    '''You should reimplent the draw_vertices method to
    actually draw vertices'''
    
    def __init__(self, widget):
        vert = pkgutil.get_data("chemlab.graphics.renderers.shaders",
                                              "default_persp.vert")
        frag = pkgutil.get_data("chemlab.graphics.renderers.shaders",
                                                "default_light.frag")
        
        super(DefaultRenderer, self).__init__(widget, vert, frag)

    def draw_vertices(self):
        raise NotImplementedError()