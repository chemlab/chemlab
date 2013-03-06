import pkgutil
from .base import ShaderBaseRenderer
import numpy as np
from OpenGL.GL import *

class BoxRenderer(ShaderBaseRenderer):
    def __init__(self, viewer, vectors):
        '''Used to render a wireframe cube centered in the origin and of
        edge length *dim*.

        '''
        vert = pkgutil.get_data("chemlab.graphics.renderers.shaders",
                                "default_persp.vert")
        frag = pkgutil.get_data("chemlab.graphics.renderers.shaders",
                                "no_light.frag")

        super(BoxRenderer, self).__init__(viewer, vert, frag)
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
        
        glColor3f(0, 0, 0)
        glBegin(GL_LINES)
        for i in lines_vertices:
            glVertex3f(*i)
        glEnd()
        
    
    def update(self, vectors):
        self.vectors = vectors
