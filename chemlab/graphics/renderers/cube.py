import pyglet

from .base import AbstractRenderer

class CubeRenderer(AbstractRenderer):
    def __init__(self, dim):
        '''Used to render a wireframe cube centered in the origin and of
        edge length *dim*.

        '''
        self.dim = dim
        
    def draw(self):
        l = self.dim
        x = l*0.5 
        pyglet.graphics.draw(8*3, pyglet.gl.GL_LINES,
                             # Front Square
                       ("v3f", (x, x, x,  -x, x, x,
                                -x, x, x, -x, -x, x,
                                -x, -x, x, x, -x, x,
                                x, -x, x,  x, x, x,
                                # Back Square
                                x, x, -x,  -x, x, -x,
                                -x, x, -x, -x, -x, -x,
                                -x, -x, -x, x, -x, -x,
                                x, -x, -x,  x, x, -x,
                                # Connecting the two squares
                                x,x,x, x,x,-x,
                                -x,x,x, -x,x,-x,
                                -x,-x,x, -x,-x,-x,
                                x,-x,x, x,-x, -x)),
                             ("n3f", (0.0,)*24*3))
    
    def update(self, boxsize):
        self.dim = boxsize
