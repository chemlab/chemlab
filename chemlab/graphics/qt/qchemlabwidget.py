from __future__ import division

import numpy as np
import time

from PIL import Image as pil_Image

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import  Qt
from PyQt4.QtOpenGL import QGLWidget

from OpenGL.GL import *
from OpenGL.GL.framebufferobjects import *

from ..camera import Camera
from ..textures import Texture
from .. import colors

DEFAULT_FRAMEBUFFER = 0

class QChemlabWidget(QGLWidget):
    '''Extensible and modular OpenGL widget developed using the Qt (PyQt4)
    Framework. This widget can be used in other PyQt4 programs.

    The widget by itself doesn't draw anything, it delegates the
    writing task to external components called 'renderers' that expose
    the interface found in
    :py:class:`~chemlab.graphics.renderers.base.AbstractRenderer`. Renderers
    are responsible for drawing objects in space and have access to their
    parent widget.

    To attach a renderer to QChemlabWidget you can simply append it
    to the ``renderers`` attribute::

        from chemlab.graphics.qt import QChemlabWidget
        from chemlab.graphics.renderers import SphereRenderer

        widget = QChemlabWidget()
        widget.renderers.append(SphereRenderer(widget, ...))

    You can also add other elements for the scene such as user interface
    elements, for example some text. This is done in a way similar to
    renderers::

        from chemlab.graphics.qt import QChemlabWidget
        from chemlab.graphics.uis import TextUI

        widget = QChemlabWidget()
        widget.uis.append(TextUI(widget, 200, 200, 'Hello, world!'))

    .. warning:: At this point there is only one ui element available.
                PyQt4 provides a lot of UI elements so there's the
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

    clicked = QtCore.pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super(QChemlabWidget, self).__init__(*args, **kwargs)

        # Renderers are responsible for actually drawing stuff
        self.renderers = []

        # Ui elements represent user interactions
        self.uis = []

        # Post processing
        self.post_processing = []

        self.light_dir = np.array([0.0, 0.0, 1.0])
        self.background_color = colors.white

        self.camera = Camera()
        self.camera.aspectratio = float(self.width()) / self.height()

    def sizeHint(self):
        return QtCore.QSize(800, 600)

    def minimumSizeHint(self):
        return QtCore.QSize(600, 600)

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_MULTISAMPLE)

        # Those are the post-processing buffers
        self.fb0, self.fb1, self.fb2 = glGenFramebuffers(3)

        self.textures = {'color': create_color_texture(self.fb0, self.width(), self.height()),
                         'depth': create_depth_texture(self.fb0, self.width(), self.height()),
                         'normal': create_normal_texture(self.fb0, self.width(), self.height())}



        glDrawBuffers(2, np.array([GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1], dtype='uint32'))

        if (glCheckFramebufferStatus(GL_FRAMEBUFFER)
            != GL_FRAMEBUFFER_COMPLETE):
            raise Exception('Framebuffer is not complete')

        self._extra_textures = {'fb1': create_color_texture(self.fb1, self.width(), self.height()),
                                'fb2': create_color_texture(self.fb2, self.width(), self.height())}


    def paintGL(self):
        '''GL function called each time a frame is drawn'''

        if self.post_processing:
            # Render to the first framebuffer
            glBindFramebuffer(GL_FRAMEBUFFER, self.fb0)
            glViewport(0, 0, self.width(), self.height())

            status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
            if (status != GL_FRAMEBUFFER_COMPLETE):
                reason = dict(GL_FRAMEBUFFER_UNDEFINED='UNDEFINED',
                              GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT='INCOMPLETE_ATTACHMENT',
                              GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT='INCOMPLETE_MISSING_ATTACHMENT',
                              GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER='INCOMPLETE_DRAW_BUFFER',
                              GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER='INCOMPLETE_READ_BUFFER',
                              GL_FRAMEBUFFER_UNSUPPORTED='UNSUPPORTED',
                          )[status]

                raise Exception('Framebuffer is not complete: {}'.format(reason))
        else:
            glBindFramebuffer(GL_FRAMEBUFFER, DEFAULT_FRAMEBUFFER)


        # Clear color take floats
        bg_r, bg_g, bg_b, bg_a = self.background_color
        glClearColor(bg_r/255, bg_g/255, bg_b/255, bg_a/255)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        proj = self.camera.projection
        cam = self.camera.matrix

        self.mvproj = np.dot(proj, cam)

        self.ldir = cam[:3, :3].T.dot(self.light_dir)



        # Draw World
        self.on_draw_world()

        # Iterate over all of the post processing effects
        if self.post_processing:
            if len(self.post_processing) > 1:
                newarg = self.textures.copy()

                # Ping-pong framebuffer rendering
                for i, pp in enumerate(self.post_processing[:-1]):
                    if i % 2:
                        outfb = self.fb1
                        outtex = self._extra_textures['fb1']
                    else:
                        outfb = self.fb2
                        outtex = self._extra_textures['fb2']

                    pp.render(outfb, newarg)

                    newarg['color'] = outtex

                self.post_processing[-1].render(DEFAULT_FRAMEBUFFER, newarg)

            else:
                self.post_processing[0].render(DEFAULT_FRAMEBUFFER, self.textures)

        # Draw the UI at the very last step
        self.on_draw_ui()

    def resizeGL(self, w, h):

        glViewport(0, 0, w, h)
        self.camera.aspectratio = float(self.width()) / self.height()

        if self.post_processing:
            # We have to recreate all of our textures
            self.textures['color'].delete()
            self.textures['depth'].delete()
            self.textures['normal'].delete()

            self.textures = {'color': create_color_texture(self.fb0, self.width(), self.height()),
                             'depth': create_depth_texture(self.fb0, self.width(), self.height()),
                             'normal': create_normal_texture(self.fb0, self.width(), self.height())}
            glDrawBuffers(2, np.array([GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1], dtype='uint32'))


            self._extra_textures['fb1'].delete()
            self._extra_textures['fb2'].delete()

            self._extra_textures = {'fb1': create_color_texture(self.fb1, self.width(), self.height()),
                                    'fb2': create_color_texture(self.fb2, self.width(), self.height())}

            # The post-processing effect can have something to do as well
            for p in self.post_processing:
                p.on_resize(w, h)

    def on_draw_ui(self):
        for u in self.uis:
            u.draw()

    def on_draw_world(self):
        for r in self.renderers:
            r.draw()

    def wheelEvent(self, evt):
        z = evt.delta()
        self.camera.mouse_zoom(z*0.01)

        self.update()

    def mousePressEvent(self, evt):
        self._clickstart = time.time()
        self._last_mouse_right = evt.button() == Qt.RightButton
        self._last_mouse_left = evt.button() == Qt.LeftButton

        self._last_mouse_pos = evt.pos()

    def mouseReleaseEvent(self, evt):
        if  time.time() - self._clickstart < 0.2:
            self.clicked.emit(evt)

    def screen_to_normalized(self, x, y):
        w = self.width()
        h = self.height()
        return  2*float(x)/w - 1.0, 1.0 - 2*float(y)/h

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
                self.update()

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

                self.update()

    def toimage(self, width=None, height=None):
        '''Return the current scene as a PIL Image.

        **Example**

        You can build your molecular viewer as usual and dump an image
        at any resolution supported by the video card (up to the
        memory limits)::

            v = QtViewer()

            # Add the renderers
            v.add_renderer(...)

            # Add post processing effects
            v.add_post_processing(...)

            # Move the camera
            v.widget.camera.autozoom(...)
            v.widget.camera.orbit_x(...)
            v.widget.camera.orbit_y(...)

            # Save the image
            image = v.widget.toimage(1024, 768)
            image.save("mol.png")


        .. seealso::

            https://pillow.readthedocs.org/en/latest/PIL.html#module-PIL.Image

        '''
        from .postprocessing import NoEffect
        effect = NoEffect(self)

        self.post_processing.append(effect)

        oldwidth, oldheight = self.width(), self.height()

        #self.initializeGL()

        if None not in (width, height):
            self.resize(width, height)
            self.resizeGL(width, height)
        else:
            width = self.width()
            height = self.height()

        self.paintGL()
        self.post_processing.remove(effect)
        coltex = effect.texture
        coltex.bind()
        glActiveTexture(GL_TEXTURE0)
        data = glGetTexImage(GL_TEXTURE_2D, 0, GL_RGBA, GL_UNSIGNED_BYTE)
        image = pil_Image.frombuffer('RGBA', (width, height), data, 'raw', 'RGBA', 0, -1)

        #self.resize(oldwidth, oldheight)
        #self.resizeGL(oldwidth, oldheight)

        return image

def create_color_texture(fb, width, height):
    texture = Texture(GL_TEXTURE_2D, width, height, GL_RGBA, GL_RGBA,
                      GL_UNSIGNED_BYTE)

    # Set some parameters
    texture.set_parameter(GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    texture.set_parameter(GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    glBindFramebuffer(GL_FRAMEBUFFER, fb)
    glViewport(0, 0, width, height)

    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D,
                           texture.id, 0)

    return texture

def create_depth_texture(fb, width, height):
    texture = Texture(GL_TEXTURE_2D, width, height, GL_DEPTH_COMPONENT24,
                      GL_DEPTH_COMPONENT, GL_FLOAT)

    texture.set_parameter(GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    texture.set_parameter(GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    glBindFramebuffer(GL_FRAMEBUFFER, fb)
    glViewport(0, 0, width, height)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D,
                           texture.id, 0)

    return texture


def create_normal_texture(fb, width, height):
    texture = Texture(GL_TEXTURE_2D, width, height, GL_RGB, GL_RGB,
                      GL_UNSIGNED_BYTE)

    texture.set_parameter(GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    texture.set_parameter(GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    glBindFramebuffer(GL_FRAMEBUFFER, fb)
    glViewport(0, 0, width, height)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT1, GL_TEXTURE_2D,
                           texture.id, 0)

    return texture
