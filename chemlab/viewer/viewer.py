import pyglet
from pyglet.gl import *
from world import Widget
import artist as art

class Viewer(Widget):

    @property
    def molecule(self):
        return self.__molecule
    
    @molecule.setter
    def molecule(self, mol):
        self.__molecule = mol
        
        self._centre = sum(at.coords for at in mol.atoms) / len(mol.atoms)
    
    def on_draw_scene(self):
        
        # Move to the geometric center
        glTranslatef(*-self._centre)
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

