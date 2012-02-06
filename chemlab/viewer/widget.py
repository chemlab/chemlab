from OpenGL.GLUT import *
import pyglet

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


class PyGletWidget(pyglet.window.Window):

    def __init__(self):
        super(PyGletWidget,self).__init__()
        self.width = 500
        self.height = 600 
    
    def on_draw(self):
        self.display()

    def swap_buffers(self):
        self.flip()

    def refresh(self):
        self.on_draw()

    def main(self):
        pyglet.app.run()
    