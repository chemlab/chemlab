import pyglet
from pyglet.gl import *
from world import Widget, Widget2
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

from ..gletools.shapes import Cylinder, Sphere, Arrow
from . import colors
import numpy as np
import pyglet

HIGHRES = 5

class Viewer2(Widget2):
    def __init__(self):
        super(Viewer2, self).__init__()
        self._shapes = []

        
    @property
    def molecule(self):
        return self._molecule 
    @molecule.setter
    def molecule(self, molecule):
        self._molecule = molecule
        
        self._shapes = []
        for atom in molecule.atoms:
            color = colors.map.get(atom.type, colors.light_grey)
            s = Sphere(0.4, atom.coords, color=color, parallels=HIGHRES, meridians=HIGHRES)
            self._shapes.append(s)
            
        for bond in molecule.bonds:
            a = Cylinder(0.1, bond.end.coords, bond.start.coords, cloves=HIGHRES)
            self._shapes.append(a)

    def on_draw_world(self):
        for s in self._shapes:
            s.draw()
