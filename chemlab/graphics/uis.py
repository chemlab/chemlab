from OpenGL.GL import *
from PySide.QtGui import QFont, QPainter

class TextUI(object):
    def __init__(self, viewer, x, y, text):
        self.viewer = viewer
        w, h = viewer.width(), viewer.height()
        self.x, self.y = x, y
        self.text = text
        
    def draw(self):
        glUseProgram(0)
        glLoadIdentity()
        glColor3f(0.0, 0.0, 0.0)
        self.viewer.renderText(self.x, self.y, self.text, QFont('Ubuntu', 36))
        
    def update_text(self, text):
        self.text = text