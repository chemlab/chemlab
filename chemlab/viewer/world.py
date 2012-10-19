from pyglet.gl import *
import pyglet
from pyglet.window import key
from trackball_camera import TrackballCamera
import numpy as np
from shaders import default_program
from ..gletools.transformations import simple_clip_matrix
from ..gletools.camera import Camera
GLfloat_4 = GLfloat * 4

DT_SMOOTH = 1.0 / 60

def norm1(x,maxx):
    """given x within [0,maxx], scale to a range [-1,1]."""
    return (2.0 * x - float(maxx)) / float(maxx)

def unproject(x, y, z, height):
    modelview = (GLdouble * 16)()
    glGetDoublev(GL_MODELVIEW_MATRIX, modelview)
    project = (GLdouble * 16)()
    glGetDoublev(GL_PROJECTION_MATRIX, project)
    viewport = (GLint * 4)()
    glGetIntegerv(GL_VIEWPORT, viewport)
    xret, yret, zret = GLdouble(), GLdouble(), GLdouble()
    gluUnProject(x, height - y, z,
                 modelview,
                 project,
                 viewport,
                 byref(xret), byref(yret), byref(zret))
    
    return xret.value, yret.value, zret.value

class PanningCamera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self._center = [0.0, 0.0, 0.0]

        self.x = 0
        self.y = 0
        self.dx = 0
        self.dy = 0
        
    def mouse_move(self, x, y, dx, dy):
        
        self.x, self.y = x, y
        self.dx, self.dy = dx, dy

    def reset(self):
        self.x = self.y = self.dx = self.dy = 0.0

    def before_rotation(self):
        x_start, y_start, z_start = unproject(self.x, self.y, 1.0,
                                              self.height)
        
        x_end, y_end, z_end = unproject(self.x + self.dx, self.y + self.dy, 1.0,
                                        self.height)
        
        self._center[0] += float(x_end - x_start) * 0.1
        self._center[1] += -float(y_end - y_start) * 0.1
        self._center[2] += float(z_end - z_start) * 0.1
        
        
    def update_modelview(self, invert=False):
        x, y, z = self._center
        if invert:
            glTranslatef(-x, -y, -z)
        else:
            glTranslatef(*self._center)
        
    
    
class Widget(pyglet.window.Window):
    """It's a subclass of pyglet.window.Window, it does the infamous
    job of setting up the world, including camera handling, resize
    handling and basic input events.

    """

    def __init__(self):
        super(Widget, self).__init__(resizable=True)
        self.init_materials()
        self.init_light()
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        

        self._camera_position = [0.0, 0.0, 7.0]
        self._tball = TrackballCamera(self._camera_position[2])
        self._pan = PanningCamera(self.width, self.height)
        
    def on_resize(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(50, float(self.width)/self.height, 0.1, 100)
        
    def on_draw(self):
        self.clear()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Position camera
        cm = self._camera_position
        
        glTranslatef(0.0, 0.0, -cm[2])
        
        self._pan.before_rotation()
        self._pan.update_modelview()

        self._tball.update_modelview()
        
        self.on_draw_scene()


    def init_materials(self):
        glMaterialfv(GL_FRONT, GL_AMBIENT,
                     GLfloat_4(0.2, 0.2, 0.2, 1.0))
        glMaterialfv(GL_FRONT, GL_DIFFUSE,
                     GLfloat_4(0.2, 0.2, 0.2, 1.0))
        glMaterialfv(GL_FRONT, GL_SPECULAR,
                     GLfloat_4(1.0, 1.0, 1.0, 1.0))
        glMaterialfv(GL_FRONT, GL_SHININESS,
                     GLfloat(50.0))

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if scroll_y > 0:
            self._camera_position[2] += 0.5
        else:
            self._camera_position[2] += -0.5            

    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            self._tball.mouse_roll(
                norm1(x, self.width),
                norm1(y,self.height),
                False)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.RIGHT:
            self._pan.reset()
        

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & pyglet.window.mouse.LEFT:
            self._tball.mouse_roll(
                norm1(x,self.width),
                norm1(y,self.height))
        elif buttons & pyglet.window.mouse.RIGHT:
            self._pan.mouse_move(x, y, dx, dy)

    def init_light(self):
        glLightfv(GL_LIGHT0, GL_AMBIENT, GLfloat_4(0.8, 0.8, 0.8, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, GLfloat_4(1.0, 1.0, 1.0, 1.0))
        glLightfv(GL_LIGHT0, GL_SPECULAR, GLfloat_4(1.0, 1.0, 1.0, 1.0))
        glLightfv(GL_LIGHT0, GL_POSITION, GLfloat_4(1.0, 1.0, 1.0, 0.0))   
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, GLfloat_4(0.2, 0.2, 0.2, 1.0))
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        

class Widget2(pyglet.window.Window):
    def __init__(self):
        super(Widget2, self).__init__(resizable=True)

        # Set light direction
        
        self._keys = key.KeyStateHandler()
        self.push_handlers(self._keys)
        self._camera = Camera()
        self._camera.moveto(np.array([0.0, 0.0, -5.0]))
        
        self._aspectratio = float(self.width) / self.height
        self.fps_display = pyglet.clock.ClockDisplay()
        glEnable(GL_MULTISAMPLE)
    
    def on_draw(self):
        # Set Background
        glClearColor(1.0, 1.0, 1.0, 1.0)
        self.clear()
        
        label = pyglet.text.Label('Hello, world',
                                  font_name='Times New Roman',
                                  font_size=36,
                                  x=10, y=10, color=(0, 0, 0, 255))
        
        #label.draw()
        self.fps_display.draw()
        # Set Perspective
        self._projection_matrix = simple_clip_matrix(
            1, 0.1, 100, self._aspectratio)
        
        proj = np.asmatrix(self._projection_matrix)
        cam = np.asmatrix(self._camera.matrix)
        
        default_program.vars.mvproj = np.array(np.dot(proj, cam))
        default_program.vars.lightDir = np.array([0.0, 0.0, 1.0])

        # Draw UI
        self.draw_ui()
        
        # Draw World
        with default_program:
            glEnable(GL_DEPTH_TEST)
            glDepthFunc(GL_LESS)
            self.on_draw_world()
        
    # Events that handle the camera
    def on_key_press(self, symbol, modifiers):
        def update_cam(dt):
            anydown = False
            if self._keys[key.RIGHT]:
                anydown = True
                self._camera.orbit(-0.3, 0)
                
            if self._keys[key.LEFT]:
                anydown = True
                self._camera.orbit(0.3, 0)
                
            if self._keys[key.UP]:
                anydown = True
                self._camera.orbit(0, 0.3)
                
            if self._keys[key.DOWN]:
                anydown = True
                self._camera.orbit(0, -0.3)
                
            if not anydown:
                pyglet.clock.unschedule(update_cam)
        if symbol in (key.RIGHT, key.LEFT, key.UP, key.DOWN):
            pyglet.clock.schedule(update_cam)

    # Methods that needs to be impelemented by subclasses
    def draw_ui(self):
        pass
    
    def on_draw_world(self):
        pass
        
        
    
