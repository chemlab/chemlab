from OpenGL.GL import (shaders,
                       GL_VERTEX_SHADER, GL_FRAGMENT_SHADER,
                       glGetUniformLocation, glUseProgram, GL_FALSE,
glUniform3f, glUniformMatrix4fv, GLfloat, GL_TRUE)
from ctypes import POINTER
import numpy as np
import pkgutil

def set_uniform(prog, uni, typ, value):
    location = glGetUniformLocation(prog, uni)
    if typ == '1f':
        glUniform1f(location, value)
    if typ == '3f':
        glUniform3f(location, *value)
    if type == '4f':
        glUniform3f(location, *value)
    if typ == '4fv':
        glUniformMatrix4fv(location, 1, GL_TRUE, value.astype(np.float32))

class AbstractRenderer(object):
    '''An AbstractRenderer is an interface for Renderers. Each
    renderer have to implement an initialization function __init__, a
    draw method to do the actual drawing and an update function, that
    is used to update the data to be displayed.

    '''
    def __init__(self, *args, **kwargs):

        self.VERTEX_SHADER = pkgutil.get_data("chemlab.graphics.renderers.shaders",
                                              "default_persp.vert")
        self.FRAGMENT_SHADER = pkgutil.get_data("chemlab.graphics.renderers.shaders",
                                                "default_light.frag")
        
        
    def draw(self):
        pass
    
    def update(self, *args, **kwargs):
        pass
    
    def set_viewer(self, v):
        self.viewer = v
    
    def compile_shader(self):
        vertex = shaders.compileShader(self.VERTEX_SHADER,GL_VERTEX_SHADER)
        fragment = shaders.compileShader(self.FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
        
        self.shader = shaders.compileProgram(vertex, fragment)

    def setup_shader(self):
        glUseProgram(self.shader)
        # Setup the uniforms
        set_uniform(self.shader, "mvproj", "4fv", self.viewer.mvproj)
        set_uniform(self.shader, "lightDir", "3f", self.viewer.ldir)
        set_uniform(self.shader, "camera", "3f", self.viewer.camera.position)

