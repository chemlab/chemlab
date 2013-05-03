from OpenGL.GL import *
import numpy as np

def set_uniform(prog, uni, typ, value):
    location = glGetUniformLocation(prog, uni)
    if typ == '1f':
        glUniform1f(location, value)
    elif typ == '3f':
        glUniform3f(location, *value)
    elif type == '4f':
        glUniform4f(location, *value)
    elif typ == 'mat4fv':
        glUniformMatrix4fv(location, 1, GL_TRUE, value.astype(np.float32))
