# Gamma correction effect
import numpy as np
import os

from OpenGL.GL import *
from OpenGL.GL.framebufferobjects import *
from OpenGL.arrays import vbo

from ..textures import Texture
from ..shaders import compileShader
from .base import AbstractEffect

class GammaCorrectionEffect(AbstractEffect):
    '''Add gamma correction to the current scene.
    
    Scenes displayed by OpenGL are in RGB color space. The response to
    colors by our eyes (and by old CRT screens) is not linear, in
    other words, we perceive better dark tones than light tones. As a
    result, the image produced is usually too dark.

    To offset this effect you can apply gamma correction. The correct
    value is screen-dependent but it is usually between 1.8 and
    2.5. You can tweak this parameter through the parameter *gamma*.

    .. image:: /_static/gamma_on_off.png
        :width: 800px
    
    '''
    
    def __init__(self, widget, gamma=2.2):
        self.widget = widget
        curdir = os.path.dirname(__file__)
        
        vert = open(os.path.join(curdir, 'shaders', 'noeffect.vert')).read()
        frag = open(os.path.join(curdir, 'shaders', 'gamma.frag')).read()        
        
        # Compile quad shader
        vertex = compileShader(vert, GL_VERTEX_SHADER)
        fragment = compileShader(frag, GL_FRAGMENT_SHADER)
        self.gamma = gamma
        self.quad_program = shaders.compileProgram(vertex, fragment)

    def render(self, fb, textures):
        # We need to render to a quad
        glBindFramebuffer(GL_FRAMEBUFFER, fb)
        glViewport(0, 0, self.widget.width(), self.widget.height())
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glUseProgram(self.quad_program)
        
        qd_id = glGetUniformLocation(self.quad_program, b"rendered_texture")
        # Setting up the texture
        glActiveTexture(GL_TEXTURE0)
        textures['color'].bind()
        # Set our "rendered_texture" sampler to user Texture Unit 0
        glUniform1i(qd_id, 0)
        
        # Set resolution
        glUniform2f(glGetUniformLocation(self.quad_program, b'resolution'), self.widget.width(), self.widget.height())
        # Set gamma value
        glUniform1f(glGetUniformLocation(self.quad_program, b'gamma'), self.gamma)
        
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