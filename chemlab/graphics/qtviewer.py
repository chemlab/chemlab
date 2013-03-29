import numpy as np
import time

from PySide.QtGui import QMainWindow, QApplication
from PySide.QtCore import QTimer, Qt
from PySide import QtCore, QtGui
from PySide.QtOpenGL import *

from .qchemlabwidget import QChemlabWidget


app = QApplication([])

class FpsDraw(object):
    def __init__(self, parent):
        self.ctimer = QTimer()
        self.ctimer.start(0)
        self.parent = parent
        self.prev = time.time()
        self.ctimer.timeout.connect(self.parent.glDraw)
    
    def draw(self):
        self.cur = time.time()
        elapsed = self.cur - self.prev
        self.prev = self.cur
        self.parent.renderText(50, 50, '%f' % (1/elapsed) )
        

class QtViewer(QMainWindow):
    """Bases: `PySide.QtGui.QMainWindow`

    View objects in space.

    This class can be used to build your own visualization routines by
    attaching :doc:`renderers <chemlab.graphics.renderers>`  and
    :doc:`uis <chemlab.graphics.uis>` to it.
    
    .. seealso:: :doc:`/graphics`
    
    **Example**
    
    In this example we can draw 3 blue dots and some overlay text::

        from chemlab.graphics import QtViewer
        from chemlab.graphics.renderers import PointRenderer
        from chemlab.graphics.uis import TextUI
         
        vertices = [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [2.0, 0.0, 0.0]]
        blue = (0, 255, 255, 255)
         
        colors = [blue,] * 3
         
        v = QtViewer()
         
        pr = v.add_renderer(PointRenderer, vertices, colors)
        tu = v.add_ui(TextUI, 100, 100, 'Hello, world!')
         
        v.run()
    
    """
    
    def __init__(self):
        QMainWindow.__init__(self)
        widget = QChemlabWidget(self)
        self.setCentralWidget(widget)
        self.resize(1000, 800)
        self.widget = widget
        self.show()
        
    def run(self):
        '''Display the QtViewer

        '''
        app.exec_()
        
    def schedule(self, callback, timeout=100):
        '''Schedule a function to be called repeated time.

        This method can be used to perform animations.
        
        **Example**
        
        This is a typical way to perform an animation, just::
        
            from chemlab.graphics import QtViewer
            from chemlab.graphics.renderers import SphereRenderer
            
            v = QtViewer()
            sr = v.add_renderer(SphereRenderer, centers, radii, colors)
             
            def update():
               # calculate new_positions
               sr.update_positions(new_positions)
               v.widget.repaint()
            
            v.schedule(update)
            v.run()
        
        .. note:: remember to call QtViewer.widget.repaint() each
                  once you want to update the display.
        

        **Parameters**
        
        callback: function()
            A function that takes no arguments that will be 
            called at intervals.
        timeout: int
            Time in milliseconds between calls of the *callback*
            function.

        **Returns**
        a `QTimer`, to stop the animation you can use `Qtimer.stop`
        '''
        timer = QTimer(self)
        timer.timeout.connect(callback)
        timer.start(timeout)
        return timer
        
    def add_renderer(self, klass, *args, **kwargs):
        '''Add a renderer to the current scene.
        
        **Parameter**
        
        klass: renderer class
            The renderer class to be added
        args, kwargs:
            Arguments used by the renderer constructor,
            except for the *widget* argument.
        
        .. seealso:: :py:class:`~chemlab.graphics.renderers.AbstractRenderer`

        **Return**

        The istantiated renderer. You should keep the return value to
        be able to update the renderer at run-time.

        '''
        renderer = klass(self.widget, *args, **kwargs)
        self.widget.renderers.append(renderer)
        return renderer
    
    def add_ui(self, klass, *args, **kwargs):
        '''Add an UI element for the current scene. The approach is
        the same as renderers.

        .. warning:: The UI api is not yet finalized

        '''
        ui = klass(self.widget, *args, **kwargs)
        self.widget.uis.append(ui)
        return ui
        
    # Events
    def keyPressEvent(self, evt):
        
        angvel = 0.3
        
        if evt.key() == Qt.Key_Up:
            self.widget.camera.orbit_x(angvel)
            
        if evt.key() == Qt.Key_Down:
            self.widget.camera.orbit_x(-angvel)
            
        if evt.key() == Qt.Key_Left:
            self.widget.camera.orbit_y(-angvel)
            
        if evt.key() == Qt.Key_Right:
            self.widget.camera.orbit_y(angvel)
        
        if evt.key() == Qt.Key_Plus:
            self.widget.camera.mouse_zoom(0.1)
        if evt.key() == Qt.Key_Minus:
            self.widget.camera.mouse_zoom(-0.1)

        self.widget.repaint()

if __name__ == '__main__':
    QtViewer().run()

