from OpenGL.GL import *
import numpy as np

def set_uniform(prog, uni, typ, value):
    location = glGetUniformLocation(prog, uni)
    if typ == '1f':
        glUniform1f(location, value)
    if typ == '3f':
        glUniform3f(location, *value)
    if type == '4f':
        glUniform4f(location, *value)
    if typ == 'mat4fv':
        glUniformMatrix4fv(location, 1, GL_TRUE, value.astype(np.float32))
