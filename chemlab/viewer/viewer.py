import pyglet
from pyglet.gl import *
from world import Widget
import artist as art

class Viewer(Widget):
    
    def on_draw_scene(self):
        art.draw_molecule(self.molecule)

    def show(self):
        pyglet.app.run()



