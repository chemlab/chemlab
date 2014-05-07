from OpenGL.GL import *
from PySide.QtGui import QFont, QPainter

import ImageFont # From PIL

def setup_textures():
    # Make the text atlas using freetype
    font_name = 'Arial.ttf'
    height = 40
    nglyphs = 128
    ft = ImageFont.truetype(font_name, height)
    
    # 128 Glyphs
    textures = [None] * nglyphs
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
        height = next_p2 (glyph_height + 1)

        # We put the pixel data in an awesome, encompassing string of
        # 0,1
        expanded_data = ""
        for j in xrange (height):
            for i in xrange (width):
                if (i >= glyph_width) or (j >= glyph_height):
                    value = chr (0)
                    expanded_data += value
                    expanded_data += value
                else:
                    value = chr (glyph.getpixel ((i, j)))
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
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, width, height,
                      border, GL_LUMINANCE_ALPHA,
                      GL_UNSIGNED_BYTE, expanded_data )
    return textures

def next_p2 (num):
	""" If num isn't a power of 2, will return the next higher power of two """
	rval = 1
	while (rval<num):
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
        self.viewer = widget
        w, h = widget.width(), widget.height()
        self.x, self.y = x, y
        self.text = text
        
        self._tx = setup_textures()
        
    def draw(self):
        # Load the program
        # Draw a Texture
        pass
        
    def update_text(self, text):
        self.text = text
        # Setup the textures to be drawn
