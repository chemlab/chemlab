import pyglet
import numpy as np

from pyglet.gl import *
from pyglet.window import key

from .shaders import default_program
from ..gletools.transformations import simple_clip_matrix
from ..gletools.camera import Camera


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
        
        # Key pressed handling
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
        self.on_draw_ui()
        
        # Draw World
        with default_program:
            glEnable(GL_DEPTH_TEST)
            glDepthFunc(GL_LESS)
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


class RendererProxy(object):
    i = 0
    def __init__(self, ident):
        #self.input = g_input
        #self.output = g_output
        self.ident = ident
    
    def update(self, *args, **kwargs):

        g_input.put((self.ident, "update", args, kwargs))
        return g_output.get()

from chemlab.viewer.renderers import CubeRenderer, PointRenderer, SphereRenderer
from Queue import Empty
from multiprocessing import Queue, Process

def handle_renderer(v, renderer):
    ident = id(renderer)
    v.instancemap[ident] = renderer
    return RendererProxy(ident)

def handle_default(v, obj):
    return
proxymap = {CubeRenderer: handle_renderer,
            PointRenderer: handle_renderer,
            SphereRenderer: handle_renderer}

g_input = Queue()
g_output = Queue()

class ProcessViewer(AbstractViewer):
    '''ProcessViewer is a proxy that handles a Viewer from another
    process. This has the advantage to make the viewer responsive and
    asyncronous while running simulations

    '''
    def __init__(self):
        super(ProcessViewer, self).__init__()
        self.input = g_input
        self.output = g_output
        self.instancemap = {}
        
        self._p = Process(target=self._run)
        self._p.start()
        
    def _run(self):
        # Creating the first viewer instance
        v = Viewer()
        self.instancemap["main"] = v
        
        def process_signals(dt, v=v):
            try:
                # Process each input signal
                id, method, args, kwargs = g_input.get(False)
                # Setup Proxy object for return values
                res = getattr(self.instancemap[id], method)(*args, **kwargs)

                handler = proxymap.get(type(res), None)
                if handler is not None:
                    proxy = handler(self, res)
                else:
                    proxy = None
                # Return to the caller the proxy object
                self.output.put(proxy)
            except Empty:
                # No item
                return
        
        pyglet.clock.schedule(process_signals)
        pyglet.app.run()

    def add_renderer(self, *args, **kwargs):
        self.input.put(("main", "add_renderer", args, kwargs))
        proxy = self.output.get()
        return proxy

    def update(self):
        self._q.put(("update",[], {}))
    
