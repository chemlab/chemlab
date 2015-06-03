from OpenGL.GL import *
from PyQt4.QtGui import QFont, QPainter
from .shaders import compileShader, compileProgram
from OpenGL.arrays import vbo
import os
import numpy as np
try:
    import ImageFont  # From PIL
except ImportError:
    from PIL import ImageFont # From Pillow

def setup_textures():
    # Make the text atlas using freetype
    font_name = 'Arial.ttf'
    height = 48
    nglyphs = 128
    ft = ImageFont.truetype(font_name, height)

    # 128 Glyphs
    textures = [None] * nglyphs
    sizes = []
    actual_coords = []
    geometrics = []
    for i in range(nglyphs):

        ###################################################
        # Create the bitmap. Return PIL.Image.core instance
        ###################################################
        # check second arg for antialiasing
        glyph = ft.getmask((chr(i)))
        glyph_width, glyph_height = glyph.size

        # 1 pixel padding, we want only powers of two for storage
        # purposes perhaps
        width = next_p2(glyph_width + 1)
        height = next_p2(glyph_height + 1)

        # We put the pixel data in an awesome, encompassing string of
        # 0,1
        expanded_data = ""
        for j in xrange(height):
            for k in xrange(width):
                if (k >= glyph_width) or (j >= glyph_height):
                    value = chr(0)
                    expanded_data += value
                    expanded_data += value
                else:
                    value = chr(glyph.getpixel((k, j)))
                    expanded_data += value
                    expanded_data += value

        # Let's make the texture
        texture = glGenTextures(1)
        textures[i] = texture

        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        border = 0
        # Here we actually create the texture itself, notice
        # that we are using GL_LUMINANCE_ALPHA to indicate that
        # we are using 2 channel data.
        # TODO: Luminance is deprecated!!!
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height,
                     border, GL_LUMINANCE_ALPHA,
                     GL_UNSIGNED_BYTE, expanded_data)
        
        sizes.append((width, height))
        geometrics.append(ft.geometrics())
        actual_coords.append((float(glyph_width)/width,
                              float(glyph_height)/height))
        
    return dict(textures=textures, sizes=sizes, coords=actual_coords,
                geometrics=geometrics)


def next_p2(num):
    """ If num isn't a power of 2, will return the next higher power of two """
    rval = 1
    while (rval < num):
        rval <<= 1
    return rval

class TextUI(object):
    '''Display an overlay text at the point `x`, `y` in screen space.

    .. warning:: The API for this element and uis in general is not
                 yet finalized.

    **Parameters**
    
    widget:
        The parent `QChemlabWidget`
    x, y: int
        Points in screen coordinates. `x` pixels from left,
        `y` pixels from top.
    text: str
        String of text to display
    
    '''
    
    
    def __init__(self, widget, x, y, text):
        self.widget = widget
        self.res_x, self.res_y = widget.width(), widget.height()
        self.x, self.y = x, y
        self.text = text
        
        curdir = os.path.dirname(__file__)
        vert = open(os.path.join(curdir,
                                 'postprocessing',
                                 'shaders',
                                 'text.vert')).read()
        frag = open(os.path.join(curdir,
                                 'postprocessing',
                                 'shaders',
                                 'text.frag')).read()

        props = setup_textures()
        
        self._tx = props['textures']
        self._tx_sizes = props['sizes']
        self._tx_accoord = props['coords']
        self._tx_geometrics = props['geometrics']

        vertex = compileShader(vert, GL_VERTEX_SHADER)
        fragment = compileShader(frag, GL_FRAGMENT_SHADER)

        self.quad_program = shaders.compileProgram(vertex, fragment)

    def draw(self):
        self.res_x = self.widget.width()
        self.res_y = self.widget.height()
        # Load the program
        # Draw a Texture
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)

        glUseProgram(self.quad_program)
        glActiveTexture(GL_TEXTURE0)

        self.xy_ndc = np.array([(float(self.x)/self.res_x)*2 - 1,
                                (float(self.y)/self.res_y)*2 - 1], 'float32')

        offset = 0
        for c in self.text:
            texture = self._tx[ord(c)]
            w, h = self._tx_sizes[ord(c)]
            g_x, g_y = self._tx_accoord[ord(c)]
            asc, desc = self._tx_geometrics[ord(c)]

            wh_ndc = np.array([(float(w)/self.res_x)*2,
                               (float(h)/self.res_y)*2], 'float32')

            glBindTexture(GL_TEXTURE_2D, texture)
            # Set our "quad_texture" sampler to user Texture Unit 0
            qd_id = glGetUniformLocation(self.quad_program, "quad_texture")
            glUniform1i(qd_id, 0)
            # Set resolution
            res_id = glGetUniformLocation(self.quad_program, "resolution")
            glUniform2f(res_id, self.widget.width(), self.widget.height())

            origin = self.xy_ndc
            destin = wh_ndc
            origin[0] += offset
            offset = wh_ndc[0]

            destin[0] += origin[0]
            destin[1] += origin[1]

            # Let's render a quad
            quad_data = np.array([origin[0], origin[1], 0.0,
                                  destin[0], origin[1], 0.0,
                                  origin[0], destin[1], 0.0,
                                  origin[0], destin[1], 0.0,
                                  destin[0], origin[1], 0.0,
                                  destin[0], destin[1], 0.0],
                                 dtype='float32')

            vboquad = vbo.VBO(quad_data)

            tex_data = np.array([0, 0,
                                 1.0, 0,
                                 0, 1.0,
                                 0, 1.0,
                                 1.0, 0,
                                 1.0, 1.0], dtype='float32')

            vbotex = vbo.VBO(tex_data)

            vboquad.bind()
            glVertexPointer(3, GL_FLOAT, 0, None)
            glEnableClientState(GL_VERTEX_ARRAY)

            vbotex.bind()
            glTexCoordPointer(2, GL_FLOAT, 0, None)
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)

            # draw "count" points from the VBO
            glDrawArrays(GL_TRIANGLES, 0, 6)

            vboquad.unbind()
            glDisableClientState(GL_VERTEX_ARRAY)

            vbotex.unbind()
            glDisableClientState(GL_TEXTURE_COORD_ARRAY)

        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)        

    def update_text(self, text):
        self.text = text
        # Setup the textures to be drawn
