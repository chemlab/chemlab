
import pyglet
import numpy as np

from pyglet.gl import *
from pyglet.window import key
from shaders import default_program

from ..gletools.transformations import simple_clip_matrix
from ..gletools.camera import Camera

class Widget2(pyglet.window.Window):
    def __init__(self):
        super(Widget2, self).__init__(resizable=True)

        # Set light direction
        
        self._keys = key.KeyStateHandler()
        self.push_handlers(self._keys)
        self._camera = Camera()
        self._camera.moveto(np.array([0.0, 0.0, -5.0]))
        
        self._aspectratio = float(self.width) / self.height
        self.fps_display = pyglet.clock.ClockDisplay()
        glEnable(GL_MULTISAMPLE)
    
        self._zoom = 1.5
        
        # TODO Pretty brutal zoom function
        def zoom(self, inc):
            pos = self._camera.position[2]
            if (( pos < -0.1 and inc > 0) or
                ( pos > -50  and inc < 0)):
                self._camera.zoom(inc*2)
            

        # Andling keypresses
        angvel = 0.06

        kmap = { key.LEFT : (self._camera.orbit, (-angvel, 0)),
                 key.RIGHT: (self._camera.orbit, ( angvel, 0)),
                 key.UP   : (self._camera.orbit, (0,  angvel)),
                 key.DOWN : (self._camera.orbit, (0, -angvel)),
                 key.PLUS : (zoom,  (self, 0.1)),
                 key.MINUS: (zoom,  (self, -0.1))}
        
        def movement(dt):
            for k, (func, args) in kmap.items():
                if self._keys[k]:
                    func(*args)
                
        pyglet.clock.schedule(movement)
        
    def on_draw(self):
        # Set Background
        glClearColor(1.0, 1.0, 1.0, 1.0)
        self.clear()
        
        self.fps_display.draw()
        
        # Set Perspective
        self._projection_matrix = simple_clip_matrix(
            self._zoom, 0.1, 100, self._aspectratio)
        
        proj = np.asmatrix(self._projection_matrix)
        cam = np.asmatrix(self._camera.matrix)
        
        mvproj = np.array(np.dot(proj, cam))
        default_program.vars.mvproj = mvproj
        ldir =  np.dot(np.asarray(self._camera._rotation[:3,:3].T),
                       np.array([0.3, 0.2, 0.8]))
        default_program.vars.lightDir = ldir
        default_program.vars.camera = np.dot(cam[:3, :3].T, self._camera.position)
        
        # Draw UI
        self.draw_ui()
        
        # Draw World
        with default_program:
            glEnable(GL_DEPTH_TEST)
            glDepthFunc(GL_LESS)
            self.on_draw_world()
        
        
    def on_resize(self, width, height):
        super(Widget2, self).on_resize(width, height)
        self._aspectratio = float(width) / height
        
        return pyglet.event.EVENT_HANDLED
        
    # Methods that needs to be impelemented by subclasses
    def draw_ui(self):
        pass
    
    def on_draw_world(self):
        pass
        
        
    
