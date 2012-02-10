from pyglet.gl import *
import pyglet
GLfloat_4 = GLfloat * 4

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
        self._camera_position = [0.0, 0.0, -4.0]

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(90, float(self.width)/self.height, 1, 100)

    def on_draw(self):
        self.clear()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Position camera
        cm = self._camera_position
        gluLookAt(cm[0], cm[1], cm[2],
                  0.0, 0.0, 0.0,
                  0.0, 1.0, 0.0)
        
        # Rotate the scene
        
        # Draw the scene
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

    def init_light(self):
        glLightfv(GL_LIGHT0, GL_AMBIENT, GLfloat_4(0.8, 0.8, 0.8, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, GLfloat_4(1.0, 1.0, 1.0, 1.0))
        glLightfv(GL_LIGHT0, GL_SPECULAR, GLfloat_4(1.0, 1.0, 1.0, 1.0))
        glLightfv(GL_LIGHT0, GL_POSITION, GLfloat_4(1.0, 1.0, 1.0, 0.0))   
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, GLfloat_4(0.2, 0.2, 0.2, 1.0))
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
