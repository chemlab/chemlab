# TODO clean this file

from .renderers import AbstractRenderer
from .viewer import AbstractViewer, Viewer
import pyglet

from Queue import Empty
from multiprocessing import Queue, Process

g_input = Queue()
g_output = Queue()

class RendererProxy(object):
    i = 0
    def __init__(self, ident):
        self.ident = ident
    
    def update(self, *args, **kwargs):

        g_input.put((self.ident, "update", args, kwargs))
        return g_output.get()

def handle_renderer(v, renderer):
    ident = id(renderer)
    v.instancemap[ident] = renderer
    return RendererProxy(ident)

def handle_default(v, obj):
    return

proxymap = {AbstractRenderer: handle_renderer}

import os
import signal

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

        
        self._main_pid = os.getpid()
        
        self._p = Process(target=self._run)
        self._p.start()
    def _run(self):
        # Creating the first viewer instance
        opt = pyglet.options
        reload(pyglet)
        pyglet.options = opt
        
        v = Viewer()
        
        # When closing the window, kill both the parent and the other
        def on_close():
            curpid = os.getpid()
            os.kill(self._main_pid, signal.SIGTERM)
            os.kill(curpid, signal.SIGTERM)
        v.on_close = on_close
        
        self.instancemap["main"] = v
        
        def process_signals(dt, v=v):
            try:
                # Process each input signal
                id, method, args, kwargs = g_input.get(False)
                # Setup Proxy object for return values
                res = getattr(self.instancemap[id], method)(*args, **kwargs)

                # Getting the correct handler for the type
                handler = None
                for key, value in proxymap.items():
                    if isinstance(res, key):
                        handler = value
                        break
                
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
    
    def run(self):
        pass
        
    def join(self):
        self._p.join()