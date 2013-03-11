import numpy as np

from .camera import Camera

from PySide.QtGui import QMainWindow, QApplication
from PySide.QtCore import QTimer, Qt
from PySide.QtOpenGL import *

from OpenGL.GL import *
import numpy as np

class AbstractViewer(object):
    def add_renderer(self, renderer):
        pass

app = QApplication([])

class GLWidget(QGLWidget):
    
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
        glColor3f(1.0, 1.0, 1.0)
        
        proj = self.camera.projection
        cam = self.camera.matrix
        
        self.mvproj = mvproj = np.dot(proj, cam)
        self.ldir = np.array([0.0, 0.0, 5.0])
        
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
    
    # Events
        
    def mousePressEvent(self, evt):
        self._last_mouse_right = evt.button() == Qt.RightButton
        self._last_mouse_pos = evt.pos()
        
    def mouseMoveEvent(self, evt):
        
        if self._last_mouse_right:
            if bool(evt.buttons() & Qt.RightButton):
                point =  evt.pos() - self._last_mouse_pos
                dx, dy = point.x(), point.y()
                cam = self.widget.camera
                cam.position += (-cam.a * dx + cam.b * dy)*0.001
                cam.pivot += (-cam.a * dx + cam.b * dy)*0.001
                self.widget.repaint()
                
    def wheelEvent(self, evt):
        z = evt.delta()
        # TODO Pretty brutal zoom function
        def zoom(self, inc):
            pos = np.dot(self.camera.position, self.camera.position)**0.5
            if (( pos > 0.1 and inc > 0) or
                ( pos < 50  and inc < 0)):
                self.camera.position = self.camera.position - self.camera.position*inc/3
                
        zoom(self.widget, z*0.01)

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
        def zoom(self, inc):
            pos = np.dot(self.camera.position, self.camera.position)**0.5
            if (( pos > 0.1 and inc > 0) or
                ( pos < 50  and inc < 0)):
                self.camera.position = self.camera.position - self.camera.position*inc/3
                
        if evt.key() == Qt.Key_Plus:
            zoom(self.widget, 0.1)
        if evt.key() == Qt.Key_Minus:
            zoom(self.widget, -0.1)

        self.widget.repaint()

if __name__ == '__main__':
    QtViewer().run()

