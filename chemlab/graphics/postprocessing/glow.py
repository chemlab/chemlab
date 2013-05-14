'''Glow effect

'''
from ..textures import Texture

from OpenGL.GL import *
from OpenGL.GL.framebufferobjects import *
from OpenGL.arrays import vbo

import numpy as np
import numpy.linalg as LA
import os
from random import uniform
from ..transformations import normalized
from ..shaders import set_uniform

class GlowEffect(object):
    
    def __init__(self, widget):
        self.widget = widget
        curdir = os.path.dirname(__file__)

        # Setup SSAO program
        vert = open(os.path.join(curdir, 'shaders', 'noeffect.vert')).read()
        frag = open(os.path.join(curdir, 'shaders', 'glow1.frag')).read()        
        
        # Compile quad shader
        vertex = shaders.compileShader(vert, GL_VERTEX_SHADER)
        fragment = shaders.compileShader(frag, GL_FRAGMENT_SHADER)
        
        self.glow1_program = shaders.compileProgram(vertex, fragment)

        # Setup Blur program
        vert = open(os.path.join(curdir, 'shaders', 'noeffect.vert')).read()
        frag = open(os.path.join(curdir, 'shaders', 'glow2.frag')).read()        
        
        # Compile quad shader
        vertex = shaders.compileShader(vert, GL_VERTEX_SHADER)
        fragment = shaders.compileShader(frag, GL_FRAGMENT_SHADER)
        self.glow2_program = shaders.compileProgram(vertex, fragment)


        # Setup blend program
        vert = open(os.path.join(curdir, 'shaders', 'noeffect.vert')).read()
        frag = open(os.path.join(curdir, 'shaders', 'glow3.frag')).read()        
        
        # Compile  shader
        vertex = shaders.compileShader(vert, GL_VERTEX_SHADER)
        fragment = shaders.compileShader(frag, GL_FRAGMENT_SHADER)
        self.blend_program = shaders.compileProgram(vertex, fragment)
        
        # Intermediate framebuffer
        self.glow_fb, self.glow2_fb = glGenFramebuffers(2)
        
        # This will create the texture and setup the correct
        # resolution for the framebuffers
        self.on_resize(self.widget.width(), self.widget.height())
        
        
    def render(self, fb, textures):
        # To render the glow effect we have to do multiple step
        # 1) Render the mask (1-a)* rgb
        # 2) Render the glowing objects by using as an output value 
        #    (1 - alpha)*rgb
        #
        # 3) Blur the result
        #
        # 3) Combine the result.
        
        glBindFramebuffer(GL_FRAMEBUFFER, self.glow_fb)
        glViewport(0, 0, self.widget.width(), self.widget.height()) # ??
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glUseProgram(self.glow1_program)
        
        # Blur the result
        qd_id = glGetUniformLocation(self.glow1_program, "s_color")
        self.texture = textures['color']
        
        # Setting up the textures
        glActiveTexture(GL_TEXTURE0)
        self.texture.bind()
        glUniform1i(qd_id, 0)
        
        # Set resolution
        res_id = glGetUniformLocation(self.glow1_program, "offset")
        glUniform2f(res_id, 1.0/self.widget.width(), 1.0/self.widget.height())
        


        self.render_quad()
        
        # After the first pass, take the result, blur it again and
        # combine it with the old texture. glow2_program will do this.
        
        # Re-render on-screen by blurring the result
        glBindFramebuffer(GL_FRAMEBUFFER, self.glow2_fb)
        glViewport(0, 0, self.widget.width(), self.widget.height()) # ??
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)        
        
        glUseProgram(self.glow2_program)
        glActiveTexture(GL_TEXTURE0)
        self.glow_texture.bind()
        
        qd_id = glGetUniformLocation(self.glow2_program, "s_color")
        glUniform1i(qd_id, 0)
        
        res_id = glGetUniformLocation(self.glow2_program, "offset")
        glUniform2f(res_id, 1.0/self.widget.width(), 1.0/self.widget.height())
        glUniform1i(glGetUniformLocation(self.glow2_program, "horizontal"), 0)
        glUniform1f(glGetUniformLocation(self.glow2_program, "radius"), 4.0)        
        
        self.render_quad()
        
        # Vertical blur!
        glBindFramebuffer(GL_FRAMEBUFFER, self.glow_fb)
        glViewport(0, 0, self.widget.width(), self.widget.height()) # ??
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glUseProgram(self.glow2_program)
        
        glActiveTexture(GL_TEXTURE0)
        self.glow2_texture.bind()
        
        qd_id = glGetUniformLocation(self.glow2_program, "s_color")
        glUniform1i(qd_id, 0)
        res_id = glGetUniformLocation(self.glow2_program, "offset")
        glUniform2f(res_id, 1.0/self.widget.width(), 1.0/self.widget.height())
        glUniform1i(glGetUniformLocation(self.glow2_program, "horizontal"), 1)
        glUniform1f(glGetUniformLocation(self.glow2_program, "radius"), 4.0)       
        self.render_quad()
        
        # Blending!!
        glBindFramebuffer(GL_FRAMEBUFFER, fb)
        glViewport(0, 0, self.widget.width(), self.widget.height()) # ??
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glUseProgram(self.blend_program)
        
        glActiveTexture(GL_TEXTURE0)
        textures['color'].bind()
        glActiveTexture(GL_TEXTURE1)
        self.glow_texture.bind()
        
        glUniform1i(glGetUniformLocation(self.blend_program, "s_color1"), 0)
        glUniform1i(glGetUniformLocation(self.blend_program, "s_color2"), 1)

        res_id = glGetUniformLocation(self.blend_program, "offset")
        glUniform2f(res_id, 1.0/self.widget.width(), 1.0/self.widget.height())
        
        self.render_quad()
        
        glUseProgram(0)
        
        
        
    def render_quad(self):
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

    def on_resize(self, w, h):
        # Make the ssao-containing framebuffer, we will have to blur
        # that
        glBindFramebuffer(GL_FRAMEBUFFER, self.glow_fb)
        glViewport(0, 0, w, h)

        self.glow_texture = Texture(GL_TEXTURE_2D, self.widget.width(),
                                    self.widget.height(), GL_RGBA, GL_RGBA,
                                    GL_UNSIGNED_BYTE)

        # Set some parameters
        self.glow_texture.set_parameter(GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        self.glow_texture.set_parameter(GL_TEXTURE_MIN_FILTER, GL_LINEAR)        
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D,
                             self.glow_texture.id, 0)
        
        # Setup drawbuffers
        glDrawBuffers(1, np.array([GL_COLOR_ATTACHMENT0], dtype='uint32'))
        
        if (glCheckFramebufferStatus(GL_FRAMEBUFFER)
            != GL_FRAMEBUFFER_COMPLETE):
            print "Problem"
            return False

        glBindFramebuffer(GL_FRAMEBUFFER, self.glow2_fb)
        glViewport(0, 0, w, h)

        self.glow2_texture = Texture(GL_TEXTURE_2D, self.widget.width(),
                                    self.widget.height(), GL_RGBA, GL_RGBA,
                                    GL_UNSIGNED_BYTE)

        # Set some parameters
        self.glow2_texture.set_parameter(GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        self.glow2_texture.set_parameter(GL_TEXTURE_MIN_FILTER, GL_LINEAR)        
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D,
                             self.glow2_texture.id, 0)
        
        # Setup drawbuffers
        glDrawBuffers(1, np.array([GL_COLOR_ATTACHMENT0], dtype='uint32'))
        
        if (glCheckFramebufferStatus(GL_FRAMEBUFFER)
            != GL_FRAMEBUFFER_COMPLETE):
            print "Problem"
            return False
