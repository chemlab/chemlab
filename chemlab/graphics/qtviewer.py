import numpy as np

from .camera import Camera

from PySide.QtGui import QMainWindow, QApplication
from PySide.QtCore import QTimer, Qt
from PySide import QtCore, QtGui
from PySide.QtOpenGL import *

from OpenGL.GL import *
import numpy as np

class AbstractViewer(object):
    def add_renderer(self, renderer):
        pass

app = QApplication([])

class GLWidget(QGLWidget):
    
    def __init__(self, parent):
        super(GLWidget, self).__init__(parent)
    
    def sizeHint(self):
        return QtCore.QSize(800, 600)
        
    def minimumSizeHint(self):
        return QtCore.QSize(600, 600)
        
    def initializeGL(self):
        # Renderers are responsible for actually drawing stuff
        self._renderers = []
        
        # Ui elements represent user interactions
        self._uis = []
        
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)        
        glEnable(GL_MULTISAMPLE)
        
        self.camera = Camera()
        self.camera.aspectration = float(self.width()) / self.height()
    
    def paintGL(self):
        '''GL function called each time a frame is drawn'''
        

        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        proj = self.camera.projection
        cam = self.camera.matrix
        
        self.mvproj = mvproj = np.dot(proj, cam)
        
        self.ldir = cam[:3, :3].T.dot(np.array([0.0, 0.0, 10.0]))
        

        self.on_draw_ui()
        # Draw World
        self.on_draw_world()

         
    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        self.camera.aspectratio = float(self.width()) / self.height()
        
        
    def on_draw_ui(self):
        for u in self._uis:
            u.draw()
        
    def on_draw_world(self):
        for r in self._renderers:
            r.draw()

            
import time

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
    
    def __init__(self):
        #self.app = QApplication([])
        QMainWindow.__init__(self)
        widget = GLWidget(self)
        self.setCentralWidget(widget)
        self.resize(1000, 800)
        self.widget = widget
        self.show()
        
    def run(self):
        app.exec_()
        
    def schedule(self, callback, timeout=100):
        timer = QTimer(self)
        timer.timeout.connect(callback)
        timer.start(timeout)
        return timer
        
    def add_renderer(self, klass, *args, **kwargs):
        renderer = klass(self.widget, *args, **kwargs)
        self.widget._renderers.append(renderer)
        return renderer
    
    def add_ui(self, klass, *args, **kwargs):
        ui = klass(self.widget, *args, **kwargs)
        self.widget._uis.append(ui)
        return ui
        
    # Events
    def mousePressEvent(self, evt):
        self._last_mouse_right = evt.button() == Qt.RightButton
        self._last_mouse_left = evt.button() == Qt.LeftButton
        
        self._last_mouse_pos = evt.pos()
        
    def mouseMoveEvent(self, evt):
        
        if self._last_mouse_right:
            # Panning
            if bool(evt.buttons() & Qt.RightButton):
                x, y = self._last_mouse_pos.x(), self._last_mouse_pos.y()
                x2, y2 = evt.pos().x(), evt.pos().y()
                self._last_mouse_pos = evt.pos()
                
                # Converting to world coordinates
                w = self.widget.width()
                h = self.widget.height()
                
                x, y = 2*float(x)/w - 1.0, 1.0 - 2*float(y)/h
                x2, y2 = 2*float(x2)/w - 1.0, 1.0 - 2*float(y2)/h
                dx, dy = x2 - x, y2 - y

                cam = self.widget.camera
                
                cam.position += (-cam.a * dx  + -cam.b * dy) * 10
                cam.pivot += (-cam.a * dx + -cam.b * dy) * 10
                self.widget.repaint()
        if self._last_mouse_left:
            # Orbiting Rotation
            if bool(evt.buttons() & Qt.LeftButton):
                x, y = self._last_mouse_pos.x(), self._last_mouse_pos.y()
                x2, y2 = evt.pos().x(), evt.pos().y()
                self._last_mouse_pos = evt.pos()
                
                # Converting to world coordinates
                w = self.widget.width()
                h = self.widget.height()
                
                x, y = 2*float(x)/w - 1.0, 1.0 - 2*float(y)/h
                x2, y2 = 2*float(x2)/w - 1.0, 1.0 - 2*float(y2)/h
                dx, dy = x2 - x, y2 - y
                
                cam = self.widget.camera
                cam.mouse_rotate(dx, dy)

                self.widget.repaint()
            
                
    def wheelEvent(self, evt):
        z = evt.delta()
        self.widget.camera.mouse_zoom(z*0.01)
        
        self.widget.repaint()

        
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
        
        # TODO Pretty brutal zoom function
        if evt.key() == Qt.Key_Plus:
            self.widget.camera.mouse_zoom(0.1)
        if evt.key() == Qt.Key_Minus:
            self.widget.camera.mouse_zoom(-0.1)

        self.widget.repaint()

if __name__ == '__main__':
    QtViewer().run()

