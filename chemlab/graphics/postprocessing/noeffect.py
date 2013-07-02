import numpy as np
import os

from OpenGL.GL import *
from OpenGL.GL.framebufferobjects import *
from OpenGL.arrays import vbo

from .base import AbstractEffect

from ..textures import Texture
from ..shaders import compileShader


class NoEffect(AbstractEffect):
    '''Re-render the object without implementing any effect.

    This renderer serves as an example, and can be used to access the
    textures used for the rendering through the *texture*
    attribute.

    This texture can be used to dump the image being rendered.
    '''
    
    def __init__(self, widget):
        self.widget = widget
        curdir = os.path.dirname(__file__)
        
        vert = open(os.path.join(curdir, 'shaders', 'noeffect.vert')).read()
        frag = open(os.path.join(curdir, 'shaders', 'noeffect.frag')).read()        
        # Compile quad shader
        vertex = compileShader(vert, GL_VERTEX_SHADER)
        fragment = compileShader(frag, GL_FRAGMENT_SHADER)
        
        self.quad_program = shaders.compileProgram(vertex, fragment)
        self.texture = None
        
    def render(self, fb, textures):
        # Save the texture to be used from outside
        self.texture = textures['color']
        
        glBindFramebuffer(GL_FRAMEBUFFER, fb)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glUseProgram(self.quad_program)
        qd_id = glGetUniformLocation(self.quad_program, "quad_texture")
        
        # Setting up the texture
        glActiveTexture(GL_TEXTURE0)
        self.texture.bind()
        
        # Set our "quad_texture" sampler to user Texture Unit 0
        glUniform1i(qd_id, 0)
        # Set resolution
        res_id = glGetUniformLocation(self.quad_program, "resolution")
        glUniform2f(res_id, self.widget.width(), self.widget.height())

        # # Let's render a quad
        quad_data = np.array([-1.0, -1.0, 0.0,
                              1.0, -1.0, 0.0,
                              -1.0,  1.0, 0.0,
                              -1.0,  1.0, 0.0,
                              1.0, -1.0, 0.0,
                              1.0,  1.0, 0.0],
                             dtype='float32')
        
        vboquad = vbo.VBO(quad_data)
        vboquad.bind()
        
        glVertexPointer(3, GL_FLOAT, 0, None)        
        glEnableClientState(GL_VERTEX_ARRAY)

        # draw "count" points from the VBO
        glDrawArrays(GL_TRIANGLES, 0, 6)
        
        vboquad.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)


