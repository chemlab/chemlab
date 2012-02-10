"""Module containing interfaces with various GUI frameworks, now only the
GLUT backend is supported.

"""

from OpenGL.GLUT import *

class GLUTBackend(object):
    def __init__(self):
        glutInit(sys.argv);
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
        glutInitWindowSize(500, 600);
        glutInitWindowPosition(50,50);
        glutCreateWindow(sys.argv[0]);
        glutDisplayFunc(self.display)
        glutMotionFunc(self.move)
        glutMouseFunc(self.wheel)

    def refresh(self):
        glutPostRedisplay()
    
    def main(self):
        glutMainLoop()
    
    def swap_buffers(self):
        glutSwapBuffers()

import pyglet
from pyglet.window import Window
class PyGletBackend(Window):
    def __init__(self):
        super(PyGletBackend,self).__init__()
        
        
    def main(self):
        pyglet.app.run()

    def refresh(self):
        pass
        
    def swap_buffers(self):
        self.flip()
