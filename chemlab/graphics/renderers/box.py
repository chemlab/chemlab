from __future__ import division
import pkgutil
import numpy as np

from .base import ShaderBaseRenderer
from ..colors import black
from OpenGL.GL import *

class BoxRenderer(ShaderBaseRenderer):
    '''Used to render one wireframed box.
    
       **Parameters**
        
       widget:
          The parent QChemlabWidget
       vectors: np.ndarray((3,3), dtype=float)
          The three vectors representing the sides of the box.
       origin: np.ndarray((3,3), dtype=float), default to zero
          The origin of the box.
       color: 4 int tuple
          r,g,b,a color in the range [0,255]

    '''

    def __init__(self, widget, vectors, origin=np.zeros(3), color=black):
        vert = pkgutil.get_data("chemlab.graphics.renderers.shaders",
                                "default_persp.vert")
        frag = pkgutil.get_data("chemlab.graphics.renderers.shaders",
                                "no_light.frag")

        self.color = color
        super(BoxRenderer, self).__init__(widget, vert, frag)
        self.origin = origin
        self.vectors = vectors
        
    def draw_vertices(self):
        # We need 8 vertices to draw a box, front and back
        a, b, c = self.vectors

        f1 = c 
        f2 = c + b
        f3 = c + a + b
        f4 = c + a
        
        b1 = [0, 0, 0]
        b2 = b
        b3 = b + a
        b4 = a

        lines_vertices = np.array([
            f1, f2, f2, f3, f3, f4, f4, f1,
            b1, b2, b2, b3, b3, b4, b4, b1,
            b1, f1,
            b2, f2,
            b3, f3,
            b4, f4,
        ]) 
        
        lines_vertices += self.origin
        r, g, b, a = self.color
        
        glColor4f(r/255, g/255, b/255, a/255)
        glBegin(GL_LINES)
        for i in lines_vertices:
            glVertex3f(*i)
        glEnd()
        
    
    def update(self, vectors):
        """Update the box vectors.
        """

        self.vectors = vectors
