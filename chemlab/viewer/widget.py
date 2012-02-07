"""Module containing interfaces with various GUI frameworks, now only the
GLUT backend is supported.

"""

from OpenGL.GLUT import *

class GLUTWidget(object):
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

