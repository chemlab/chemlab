import numpy as np
import os

from OpenGL.GL import *
from OpenGL.GL.framebufferobjects import *
from OpenGL.arrays import vbo

from ..textures import Texture
from ..shaders import set_uniform, compileShader
from .base import AbstractEffect


class FXAAEffect(AbstractEffect):
    '''Fast Approximate Anti Aliasing. It is an efficient way to add
    anti-aliasing to your scenes. The reason to have it is to
    reduce jagged lines.

    The parameters *span_max*, *reduce_mul*, *reduce_min* are
    tweakable even if it is suggested to keep them at their default value.

    .. image:: /_static/fxaa_on_off.png
       :width: 800px
    
    '''
    def __init__(self, widget, span_max = 4.0, reduce_mul=1/8.0, reduce_min=1/128.0):
        self.widget = widget
        curdir = os.path.dirname(__file__)
        
        vert = open(os.path.join(curdir, 'shaders', 'noeffect.vert')).read()
        frag = open(os.path.join(curdir, 'shaders', 'fxaa.frag')).read()        
        # Compile quad shader
        vertex = compileShader(vert, GL_VERTEX_SHADER)
        fragment = compileShader(frag, GL_FRAGMENT_SHADER)
        
        self.span_max = span_max
        self.reduce_mul = reduce_mul
        self.reduce_min = reduce_min
        
        self.quad_program = shaders.compileProgram(vertex, fragment)

    def render(self, fb, texturedict):
        glBindFramebuffer(GL_FRAMEBUFFER, fb)
        glViewport(0, 0, self.widget.width(), self.widget.height())
            
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.quad_program)
        
        set_uniform(self.quad_program, 'FXAA_SPAN_MAX', '1f', self.span_max)
        set_uniform(self.quad_program, 'FXAA_REDUCE_MUL', '1f', self.reduce_mul)
        set_uniform(self.quad_program, 'FXAA_REDUCE_MIN', '1f', self.reduce_min)
        
        qd_id = glGetUniformLocation(self.quad_program, b"textureSampler")
        texture = texturedict['color']
        
        # Setting up the texture
        glActiveTexture(GL_TEXTURE0)
        texture.bind()
        
        # Set our "quad_texture" sampler to user Texture Unit 0
        glUniform1i(qd_id, 0)
        # Set resolution
        res_id = glGetUniformLocation(self.quad_program, b"texcoordOffset")
        glUniform2f(res_id, 1.0/self.widget.width(), 1.0/self.widget.height())

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
        pass