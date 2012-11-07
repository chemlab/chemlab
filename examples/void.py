import pyglet
pyglet.options['debug_gl_trace'] = True
from chemlab.graphics.viewer import Viewer


v = Viewer()
pyglet.app.run()