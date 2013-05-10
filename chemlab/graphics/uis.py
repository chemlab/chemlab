from OpenGL.GL import *
from PySide.QtGui import QFont, QPainter

class TextUI(object):
    '''Display an overlay text at the point `x`, `y` in screen space.

    .. warning:: The API for this element and uis in general is not
                 yet finalized.

    **Parameters**
    
    widget:
        The parent `QChemlabWidget`
    x, y: int
        Points in screen coordinates. `x` pixels from left,
        `y` pixels from top.
    text: str
        String of text to display
    
    '''
    
    
    def __init__(self, widget, x, y, text):
        self.viewer = widget
        w, h = widget.width(), widget.height()
        self.x, self.y = x, y
        self.text = text
        
    def draw(self):
        glUseProgram(0)
        glLoadIdentity()
        glColor3f(0.0, 0.0, 0.0)
        self.viewer.renderText(self.x, self.y, self.text, QFont('Ubuntu', 36))
        
    def update_text(self, text):
        self.text = text