'''
A post processing effect that does nothing
'''
from ..textures import Texture
from OpenGL.GL import *
from OpenGL.GL.framebufferobjects import *
from OpenGL.arrays import vbo

import numpy as np
import os

class NoEffect(object):
    
    def __init__(self, widget):
        self.widget = widget
        curdir = os.path.dirname(__file__)
        
        vert = open(os.path.join(curdir, 'shaders', 'noeffect.vert')).read()
        frag = open(os.path.join(curdir, 'shaders', 'noeffect.frag')).read()        
        # Compile quad shader
        vertex = shaders.compileShader(vert, GL_VERTEX_SHADER)
        fragment = shaders.compileShader(frag, GL_FRAGMENT_SHADER)
        
        self.quad_program = shaders.compileProgram(vertex, fragment)

        # Create the framebuffer
        self.fb = glGenFramebuffers(1)
        
        # This will create the texture and setup at the correct resolution
        self.on_resize()
        
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(0, 0, self.widget.width(), self.widget.height())
        
    def pre_render(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.fb)
        glViewport(0, 0, self.widget.width(), self.widget.height())
        
    def post_render(self):
        # We need to render to a quad
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(0, 0, self.widget.width(), self.widget.height()) # ??
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

    def on_resize(self):
        self.texture = Texture(GL_TEXTURE_2D, self.widget.width(),
                               self.widget.height(), GL_RGB, GL_RGB,
                               GL_UNSIGNED_BYTE)
        
        # Set some parameters
        self.texture.set_parameter(GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        self.texture.set_parameter(GL_TEXTURE_MIN_FILTER, GL_LINEAR)        

        # Create a texture for z buffer
        self.depth_texture = Texture(GL_TEXTURE_2D,
                                     self.widget.width(),
                                     self.widget.height(),
                                     GL_DEPTH_COMPONENT24,
                                     GL_DEPTH_COMPONENT, GL_FLOAT)
        
        self.depth_texture.set_parameter(GL_TEXTURE_MAG_FILTER,
                                         GL_NEAREST)
        self.depth_texture.set_parameter(GL_TEXTURE_MIN_FILTER,
                                         GL_LINEAR) 
        
        
        #glTexImage2D(GL_TEXTURE_2D , 0,GL_DEPTH_COMPONENT24, 1024,
        # 768, 0, GL_DEPTH_COMPONENT, GL_FLOAT, 0);
        
        glBindFramebuffer(GL_FRAMEBUFFER, self.fb)
        glViewport(0, 0, self.widget.width(), self.widget.height())
        
        glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0,
                             self.texture.id, 0)
        glFramebufferTexture(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT,
                             self.depth_texture.id, 0);

        #glDrawBuffers(1, np.array([GL_COLOR_ATTACHMENT0], dtype='uint32'))
        
        if (glCheckFramebufferStatus(GL_FRAMEBUFFER)
            != GL_FRAMEBUFFER_COMPLETE):
            print "Problem"
            return False