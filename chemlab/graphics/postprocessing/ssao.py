'''
Screen space ambient occlusion
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

class SSAOEffect(object):
    
    def __init__(self, widget, kernel_size=32, kernel_radius=2.0, ssao_power=2.0):
        self.widget = widget
        curdir = os.path.dirname(__file__)


        # Setup SSAO program
        vert = open(os.path.join(curdir, 'shaders', 'noeffect.vert')).read()
        frag = open(os.path.join(curdir, 'shaders', 'ssao.frag')).read()        
        
        # Compile quad shader
        vertex = shaders.compileShader(vert, GL_VERTEX_SHADER)
        fragment = shaders.compileShader(frag, GL_FRAGMENT_SHADER)
        
        self.ssao_program = shaders.compileProgram(vertex, fragment)

        # Setup Blur program
        vert = open(os.path.join(curdir, 'shaders', 'noeffect.vert')).read()
        frag = open(os.path.join(curdir, 'shaders', 'ssao_blur.frag')).read()        
        
        # Compile quad shader
        vertex = shaders.compileShader(vert, GL_VERTEX_SHADER)
        fragment = shaders.compileShader(frag, GL_FRAGMENT_SHADER)
        self.blur_program = shaders.compileProgram(vertex, fragment)
        
        # Create the framebuffer for the scene to draw on
        self.fb = glGenFramebuffers(1)
        
        # Framebuffer where to draw the occlusion factors and colors
        self.ssao_fb = glGenFramebuffers(1)
        
        # This will create the texture and setup the correct
        # resolution for the framebuffers
        self.on_resize()
        
        # Cleanup
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(0, 0, self.widget.width(), self.widget.height())


        # SSAO power
        self.ssao_power = ssao_power
        # Kernel sampling
        self.kernel_radius = kernel_radius
        self.kernel_size = kernel_size
        self.generate_kernel()
        
    def generate_kernel(self):
        
        self.kernel = []
        for i in range(self.kernel_size):
            randpoint = normalized([uniform(-1.0, 1.0),
                                    uniform(-1.0, 1.0),
                                    uniform(0.0, 1.0)])
            
            randpoint *= uniform(0.0, 1.0)
            # Accumulating points in the middle
            scale = float(i)/self.kernel_size
            scale = 0.1 + (1.0 - 0.1)*scale*scale # linear interpolation
            randpoint *= scale
            
            self.kernel.append(randpoint)


        
        self.kernel = np.array(self.kernel, dtype='float32')
        # Random rotations of the kernel
        self.noise_size = 4
        self.noise = []
        for i in range(self.noise_size**2):
            randpoint = normalized([uniform(-1.0, 1.0),
                                    uniform(-1.0, 1.0),
                                    0.0])
            self.noise.append(randpoint)
        self.noise = np.array(self.noise, dtype='float32')

        # Save this stuff into a small texture
        self.noise_texture = Texture(GL_TEXTURE_2D, 4, 4, GL_RGB,
                                     GL_RGB, GL_FLOAT, self.noise)
        
        self.texture.set_parameter(GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        self.texture.set_parameter(GL_TEXTURE_MIN_FILTER, GL_LINEAR)  
        
        
    def pre_render(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.fb)
        glViewport(0, 0, self.widget.width(), self.widget.height())
        
    def post_render(self):
        # We need to render to the ssao framebuffer
        # Then we will blur the result
        glBindFramebuffer(GL_FRAMEBUFFER, self.ssao_fb)
        glViewport(0, 0, self.widget.width(), self.widget.height()) # ??
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glUseProgram(self.ssao_program)
        
        qd_id = glGetUniformLocation(self.ssao_program, "quad_texture")
        normal_id = glGetUniformLocation(self.ssao_program, "normal_texture")
        depth_id = glGetUniformLocation(self.ssao_program, "depth_texture")
        noise_id = glGetUniformLocation(self.ssao_program, "noise_texture")
        
        proj = self.widget.camera.projection
        i_proj = LA.inv(proj)
        
        set_uniform(self.ssao_program, "i_proj", "mat4fv", i_proj)
        set_uniform(self.ssao_program, "proj", "mat4fv", proj)

        # Setting up the textures
        glActiveTexture(GL_TEXTURE0)
        self.texture.bind()
        
        glActiveTexture(GL_TEXTURE1)
        self.normal_texture.bind()
        
        glActiveTexture(GL_TEXTURE2)
        self.depth_texture.bind()

        glActiveTexture(GL_TEXTURE3)
        self.noise_texture.bind()
        
        # Set our "quad_texture" sampler to user Texture Unit 0
        glUniform1i(qd_id, 0)
        glUniform1i(normal_id, 1)
        glUniform1i(depth_id, 2)
        glUniform1i(noise_id, 3)

        # Set up the random kernel
        random_id = glGetUniformLocation(self.ssao_program, "random_kernel")
        glUniform3fv(random_id, self.kernel_size, self.kernel)
        
        kernel_size_id = glGetUniformLocation(self.ssao_program, "kernel_size")
        glUniform1i(kernel_size_id, self.kernel_size)
        
        kernel_radius_id = glGetUniformLocation(self.ssao_program,
                                                "kernel_radius")
        glUniform1f(kernel_radius_id, self.kernel_radius)
        ssao_power_id = glGetUniformLocation(self.ssao_program,
                                                "ssao_power")
        glUniform1f(ssao_power_id, self.ssao_power)
        
        
        # Set resolution
        res_id = glGetUniformLocation(self.ssao_program, "resolution")
        glUniform2f(res_id, self.widget.width(), self.widget.height())

        self.render_quad()

        # Re-render on-screen by blurring the result
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(0, 0, self.widget.width(), self.widget.height()) # ??
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)        
        
        glUseProgram(self.blur_program)
        glActiveTexture(GL_TEXTURE0)

        self.ssao_texture.bind()
        
        qd_id = glGetUniformLocation(self.blur_program, "quad_texture")
        glUniform1i(qd_id, 0)
        
        res_id = glGetUniformLocation(self.blur_program, "resolution")
        glUniform2f(res_id, self.widget.width(), self.widget.height())
        
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
        
        # I think we need also some new texture to have the normals!
        self.normal_texture = Texture(GL_TEXTURE_2D, self.widget.width(),
                               self.widget.height(), GL_RGB, GL_RGB,
                               GL_UNSIGNED_BYTE)
        
        # Set some parameters
        self.normal_texture.set_parameter(GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        self.normal_texture.set_parameter(GL_TEXTURE_MIN_FILTER, GL_LINEAR)        
        
        # Make the scene framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, self.fb)
        glViewport(0, 0, self.widget.width(), self.widget.height())
        
        glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0,
                             self.texture.id, 0)
        glFramebufferTexture(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT,
                             self.depth_texture.id, 0);
        
        
        
        # Attach the normal texture to the color_attachment_1
        glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT1,
                             self.normal_texture.id, 0)
        
        # Setup drawbuffers
        glDrawBuffers(2, np.array([GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1], dtype='uint32'))
        
        if (glCheckFramebufferStatus(GL_FRAMEBUFFER)
            != GL_FRAMEBUFFER_COMPLETE):
            print "Problem"
            return False
        
        # Make the ssao-containing framebuffer, we will have to blur
        # that
        
            
        glBindFramebuffer(GL_FRAMEBUFFER, self.ssao_fb)
        glViewport(0, 0, self.widget.width(), self.widget.height())


        self.ssao_texture = Texture(GL_TEXTURE_2D, self.widget.width(),
                               self.widget.height(), GL_RGBA, GL_RGBA,
                               GL_UNSIGNED_BYTE)

        # Set some parameters
        self.ssao_texture.set_parameter(GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        self.ssao_texture.set_parameter(GL_TEXTURE_MIN_FILTER, GL_LINEAR)        
        glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0,
                             self.ssao_texture.id, 0)
        
        # Setup drawbuffers
        glDrawBuffers(1, np.array([GL_COLOR_ATTACHMENT0], dtype='uint32'))
        
        if (glCheckFramebufferStatus(GL_FRAMEBUFFER)
            != GL_FRAMEBUFFER_COMPLETE):
            print "Problem"
            return False
