from OpenGL.GL import *
import numpy as np

def set_uniform(prog, uni, typ, value):
    location = glGetUniformLocation(prog, uni.encode('utf-8'))
    if typ == '1f':
        glUniform1f(location, value)
    elif typ == '3f':
        glUniform3f(location, *value)
    elif typ == '4f':
        glUniform4f(location, *value)
    elif typ == 'mat4fv':
        value = value.copy() # That was an AWFUL BUG
        glUniformMatrix4fv(location, 1, GL_TRUE, value.astype(np.float32))
    elif typ == '1i':
        glUniform1i(location, value)
    else:
        raise Exception('Unknown type function')
