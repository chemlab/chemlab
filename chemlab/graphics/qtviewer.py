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
    
    def __init__(self):
        #self.app = QApplication([])
        QMainWindow.__init__(self)
        widget = QChemlabWidget(self)
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
        self.widget.renderers.append(renderer)
        return renderer
    
    def add_ui(self, klass, *args, **kwargs):
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

