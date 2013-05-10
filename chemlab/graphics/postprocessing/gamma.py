# Gamma correction effect

'''
A post processing effect that does nothing
'''
from ..textures import Texture
from OpenGL.GL import *
from OpenGL.GL.framebufferobjects import *
from OpenGL.arrays import vbo

import numpy as np
import os

class GammaCorrectionEffect(object):
    
    def __init__(self, widget, gamma=2.2):
        self.widget = widget
        curdir = os.path.dirname(__file__)
        
        vert = open(os.path.join(curdir, 'shaders', 'noeffect.vert')).read()
        frag = open(os.path.join(curdir, 'shaders', 'gamma.frag')).read()        
        
        # Compile quad shader
        vertex = shaders.compileShader(vert, GL_VERTEX_SHADER)
        fragment = shaders.compileShader(frag, GL_FRAGMENT_SHADER)
        self.gamma = gamma
        self.quad_program = shaders.compileProgram(vertex, fragment)

    def render(self, fb, textures):
        # We need to render to a quad
        glBindFramebuffer(GL_FRAMEBUFFER, fb)
        glViewport(0, 0, self.widget.width(), self.widget.height())
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glUseProgram(self.quad_program)
        
        qd_id = glGetUniformLocation(self.quad_program, "rendered_texture")
        # Setting up the texture
        glActiveTexture(GL_TEXTURE0)
        textures['color'].bind()
        # Set our "rendered_texture" sampler to user Texture Unit 0
        glUniform1i(qd_id, 0)
        
        # Set resolution
        glUniform2f(glGetUniformLocation(self.quad_program, 'resolution'), self.widget.width(), self.widget.height())
        # Set gamma value
        glUniform1f(glGetUniformLocation(self.quad_program, 'gamma'), self.gamma)
        
        # Let's render a quad
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

    def on_resize(self, w, h):
        pass