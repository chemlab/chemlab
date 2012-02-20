import pyglet
from pyglet.gl import *
from world import Widget
import artist as art

class Viewer(Widget):

    def on_draw_scene(self):
        
        art.draw_molecule(self.molecule)

    def show(self):
        pyglet.app.run()

    def animate(self, geoms, interval = 0.1):
        self._frames = geoms
        self._curframe = 0
        self.molecule = self._frames[0]
        def update(dt):
            ln = len(self._frames)
            self.molecule = self._frames[self._curframe%ln]
            self._curframe += 1
        
        pyglet.clock.schedule_interval(update, interval)

