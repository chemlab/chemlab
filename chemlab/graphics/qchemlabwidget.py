import numpy as np

from PySide import QtCore, QtGui
from PySide.QtCore import  Qt
from PySide.QtOpenGL import QGLWidget

from OpenGL.GL import *

from .camera import Camera


class QChemlabWidget(QGLWidget):
    
    def __init__(self, parent):
        super(QChemlabWidget, self).__init__(parent)
    
    def sizeHint(self):
        return QtCore.QSize(800, 600)
        
    def minimumSizeHint(self):
        return QtCore.QSize(600, 600)
        
    def initializeGL(self):
        # Renderers are responsible for actually drawing stuff
        self.renderers = []
        
        # Ui elements represent user interactions
        self.uis = []
        
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
        for u in self.uis:
            u.draw()
        
    def on_draw_world(self):
        for r in self.renderers:
            r.draw()

    def wheelEvent(self, evt):
        z = evt.delta()
        self.camera.mouse_zoom(z*0.01)
        
        self.repaint()
            
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
                w = self.width()
                h = self.height()
                
                x, y = 2*float(x)/w - 1.0, 1.0 - 2*float(y)/h
                x2, y2 = 2*float(x2)/w - 1.0, 1.0 - 2*float(y2)/h
                dx, dy = x2 - x, y2 - y

                cam = self.camera
                
                cam.position += (-cam.a * dx  + -cam.b * dy) * 10
                cam.pivot += (-cam.a * dx + -cam.b * dy) * 10
                self.repaint()
        if self._last_mouse_left:
            # Orbiting Rotation
            if bool(evt.buttons() & Qt.LeftButton):
                x, y = self._last_mouse_pos.x(), self._last_mouse_pos.y()
                x2, y2 = evt.pos().x(), evt.pos().y()
                self._last_mouse_pos = evt.pos()
                
                # Converting to world coordinates
                w = self.width()
                h = self.height()
                
                x, y = 2*float(x)/w - 1.0, 1.0 - 2*float(y)/h
                x2, y2 = 2*float(x2)/w - 1.0, 1.0 - 2*float(y2)/h
                dx, dy = x2 - x, y2 - y
                
                cam = self.camera
                cam.mouse_rotate(dx, dy)

                self.repaint()
