'''Writing something related to the UI'''
from pyglet.graphics import draw

from pyglet import gl
import numpy as np


class RectangleUI(object):
    def __init__(self, x, y, width, height, color):
        self.width = width
        self.height = height
        self.basecolor = color
        self.secondcolor = color[:]
        self.secondcolor[0] = 0
        
        self.color = color
        self.position = [x, y]
        
        self.inside = False
        
    def draw(self):
        w = self.width
        h = self.height
        pos = self.position
        
        vertices = np.array([[0.0, 0.0],
                             [0.0, h],
                             [w, h],
                             [w, 0.0]]) + np.array(pos)
        
        draw(4, gl.GL_QUADS,
             ('v2f', vertices.flatten().tolist()),
              ('c4B', self.color * 4))

    def on_mouse_motion(self, x, y, dx, dy):
        if self.is_inside(x, y):
            self.color = self.secondcolor
            self.position[0] = x
            self.position[1] = y
        else:
            self.position[0] = x
            self.position[1] = y
            self.color = self.basecolor
        
    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.position[0] += dx
        self.position[1] += dy
    
    def is_inside(self, x, y):
        return (self.position[0] < x < self.position[0] + self.width and
                self.position[1] < y < self.position[1] + self.height)
    
    def on_click(self, x, y, key):
        # I need this event
        pass
    
    def on_drag(self, dx, dy, key):
        pass