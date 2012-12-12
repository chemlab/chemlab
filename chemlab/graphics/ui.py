'''Writing something related to the UI'''
import pyglet
from pyglet.graphics import draw
from pyglet import gl
import numpy as np

pyglet.resource.path = ['@chemlab.resources', '.']
pyglet.resource.reindex()

class Widget(pyglet.event.EventDispatcher):
    # Events: click, drag, hover
    
    
    # Subclasses should subclass this
    def is_inside(x, y):
        return False

event_types = ['on_click', 'on_drag', 'on_hover']
for e in event_types:
    Widget.register_event_type(e)

class SliderUI(Widget):
    def __init__(self, range_, x, y, width, height):
        super(SliderUI, self).__init__()
        
        self.x = x
        self.y = y
        self.range_ = range_
        
        self.rect = RectangleUI(x, y, width, height)
        cursor_im = pyglet.image.load('circle.png',
                                      file=pyglet.resource.file('circle.png'))
        self.cursor = pyglet.sprite.Sprite(cursor_im, x, y)
        self.cursor.anchor_x = self.cursor.width / 2
        self.cursor.anchor_y = self.cursor.height / 2
        
        self.binsize = binsize = float(width + float(width)/range_)/range_
        
        self.ranges = np.array([binsize*i for i in range(range_)])
        
        
        self.cursor_frame = 0
        
    def draw(self):
        self.cursor.draw()
        self.rect.draw()
        
    def is_inside(self, x, y):
        return self.rect.is_inside(x, y)

    def on_drag(self, x, y, dx, dy, button, modifiers):
        # let's bin this bastard
        import time
        snapx = np.searchsorted(self.ranges, x-self.x) - 1 
        self.cursor.x = snapx*self.binsize + self.x
        self.dispatch_event('on_update', snapx)
        
    def on_click(self, x, y, button, modifiers):
        snapx = np.searchsorted(self.ranges, x-self.x) - 1 
        self.cursor.x = snapx*self.binsize + self.x
        self.dispatch_event('on_update', snapx)

SliderUI.register_event_type('on_update')

class RectangleUI(Widget):
    def __init__(self, x, y, width, height, color=[0, 0, 0, 255]):
        '''Color in binary format'''
        super(RectangleUI, self).__init__()
        
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

    def is_inside(self, x, y):
        return (self.position[0] < x < self.position[0] + self.width and
                self.position[1] < y < self.position[1] + self.height)
    
    def on_click(self, x, y, key):
        pass
    
    def on_drag(self, dx, dy, key):
        pass