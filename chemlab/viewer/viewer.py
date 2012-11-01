import pyglet
import numpy as np

from pyglet.gl import *
from world import Widget2

class Viewer(Widget2):
    def __init__(self):
        super(Viewer, self).__init__()
        self._renderers = []
        
    def add_renderer(self, renderer):
        self._renderers.append(renderer)
    
    def on_draw_world(self):
        for r in self._renderers:
            r.draw()

    def update(self):
        for r in self._renderers:
            r.update()
