import pyglet

from .base import DefaultRenderer

class CubeRenderer(DefaultRenderer):
    def __init__(self, viewer, dim):
        '''Used to render a wireframe cube centered in the origin and of
        edge length *dim*.

        '''
        super(CubeRenderer, self).__init__(viewer)
        self.dim = dim
        
    def draw_vertices(self):
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
