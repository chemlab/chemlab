import pyglet
import numpy as np

from pyglet.gl import *
from pyglet.window import key

from .gletools.transformations import simple_clip_matrix
from .gletools.camera import Camera

class AbstractViewer(object):
    
    def add_renderer(self, renderer):
        pass

class Viewer(pyglet.window.Window, AbstractViewer):
    '''Viewer is an object used to display atoms, molecules and other
    systems. It is responsible to handle the input events and to setup
    the visualization environment (opengl etc.). The public interface
    of Viewer is defined by AbstractViewer.

    '''
    
    def __init__(self):
        super(Viewer, self).__init__(resizable=True)

        # Renderers are responsible for actually drawing stuff
        self._renderers = []
        
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)        
        glEnable(GL_MULTISAMPLE)
        
        # Key pressed handling
        self._keys = key.KeyStateHandler()
        self.push_handlers(self._keys)
        self._camera = Camera()
        self._camera.moveto(np.array([0.0, 0.0, -5.0]))
        
        self._aspectratio = float(self.width) / self.height
        self.fps_display = pyglet.clock.ClockDisplay()
        
    
        self._zoom = 1.5
        # TODO Pretty brutal zoom function
        def zoom(self, inc):
            pos = self._camera.position[2]
            if (( pos < -0.1 and inc > 0) or
                ( pos > -50  and inc < 0)):
                self._camera.zoom(inc*2)

        # Handling keypresses
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
                
        pyglet.clock.schedule_interval(movement, 1/60.0)
        
    def on_draw(self):
        from .shaders import default_program
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
        self.on_draw_ui()
        
        # Draw World
        with default_program:
            self.on_draw_world()

    def on_resize(self, width, height):
        super(Viewer, self).on_resize(width, height)
        self._aspectratio = float(width) / height
        
        return pyglet.event.EVENT_HANDLED

    def add_renderer(self, klass, *args, **kwargs):
        renderer = klass(*args, **kwargs)
        self._renderers.append(renderer)
        return renderer
    
    def on_draw_ui(self):
        pass
        
    def on_draw_world(self):
        for r in self._renderers:
            r.draw()

    def schedule(self, function, frequency=None):
        if not frequency:
            pyglet.clock.schedule(lambda t: function())
        else:
            pyglet.clock.schedule_interval(lambda t: function(), frequency)
        
    def run(self):
        pyglet.app.run()
