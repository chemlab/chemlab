from __future__ import division

import numpy as np

from PySide import QtCore, QtGui
from PySide.QtCore import  Qt
from PySide.QtOpenGL import QGLWidget

from OpenGL.GL import *

from .camera import Camera
from . import colors

class QChemlabWidget(QGLWidget):
    '''Extensible and modular OpenGL widget developed using the Qt (PySide)
    Framework. This widget can be used in other PySide programs.

    The widget by itself doesn't draw anything, it delegates the
    writing task to external components called 'renderers' that expose
    the interface found in
    :py:class:`~chemlab.graphics.renderers.base.AbstractRenderer`. Renderers
    are responsible for drawing objects in space and have access to their
    parent widget.

    To attach a renderer to QChemlabWidget you can simply append it 
    to the ``renderers`` attribute::

        from chemlab.graphics import QChemlabWidget
        from chemlab.graphics.renderers import SphereRenderer
        
        widget = QChemlabWidget()
        widget.renderers.append(SphereRenderer(widget, ...))

    You can also add other elements for the scene such as user interface
    elements, for example some text. This is done in a way similar to
    renderers::

        from chemlab.graphics import QChemlabWidget
        from chemlab.graphics.uis import TextUI
        
        widget = QChemlabWidget()
        widget.uis.append(TextUI(widget, 200, 200, 'Hello, world!'))

    .. warning:: At this point there is only one ui element available.
                PySide provides a lot of UI elements so there's the
                possibility that UI elements will be converted into renderers.
    
    QChemlabWidget has its own mouse gestures:

    - Left Mouse Drag: Orbit the scene;
    - Right Mouse Drag: Pan the scene;
    - Wheel: Zoom the scene.
    
    
    .. py:attribute:: renderers
       
       :type: list of :py:class:`~chemlab.graphics.renderers.AbstractRenderer` subclasses
     
       It is a list containing the active renderers. QChemlabWidget
       will call their ``draw`` method when appropriate. 
    
    .. py:attribute:: camera
        
        :type: :py:class:`~chemlab.graphics.camera.Camera`
        
        The camera encapsulates our viewpoint on the world. That is
        where is our position and our orientation. You should use
        on the camera to rotate, move, or zoom the scene.

    .. py:attribute:: light_dir
    
        :type: np.ndarray(3, dtype=float)
        :default: np.arrray([0.0, 0.0, 1.0])
    
        The light direction in camera space. Assume you are in the
        space looking at a certain point, your position is the
        origin. now imagine you have a lamp in your hand. *light_dir*
        is the direction this lamp is pointing. And if you move, jump,
        or rotate, the lamp will move with you.

        .. note:: With the current lighting mode there isn't a "light
             position". The light is assumed to be infinitely distant
             and light rays are all parallel to the light direction.

    .. py:attribute:: background_color

       :type: tuple 
       :default: (255, 255, 255, 255) white
    
       A 4-element (r, g, b, a) tuple that specity the background
       color. Values for r,g,b,a are in the range [0, 255]. You can
       use the colors contained in chemlab.graphics.colors.

    '''
    
    def __init__(self, parent=None):
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
        
        self.light_dir = np.array([0.0, 0.0, 1.0])
        self.background_color = colors.white
        
        
    def paintGL(self):
        '''GL function called each time a frame is drawn'''
        
        # Clear color take floats
        bg_r, bg_g, bg_b, bg_a = self.background_color
        glClearColor(bg_r/255, bg_g/255, bg_b/255, bg_a/255)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        proj = self.camera.projection
        cam = self.camera.matrix
        
        self.mvproj = mvproj = np.dot(proj, cam)
        
        self.ldir = cam[:3, :3].T.dot(self.light_dir)
        

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
