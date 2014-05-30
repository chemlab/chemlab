from OpenGL.GL import *
import numpy as np

from OpenGL.GL import shaders  # Fix autodoc

# Alias
compileProgram = shaders.compileProgram

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

# PyOpengl patching for older versions
def compileShader( source, shaderType ):
    """Compile shader source of given type
    
    source -- GLSL source-code for the shader
    shaderType -- GLenum GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, etc,
    
    returns GLuint compiled shader reference
    raises RuntimeError when a compilation failure occurs
    """
    if isinstance(source, str):
        source = [source]
    elif isinstance(source, bytes):
        source = [source.decode('utf-8')]
    
    shader = glCreateShader(shaderType)
    glShaderSource(shader, source)
    glCompileShader(shader)
    result = glGetShaderiv(shader, GL_COMPILE_STATUS)
    
    if not(result):
        # TODO: this will be wrong if the user has 
        # disabled traditional unpacking array support.
        raise RuntimeError(
            """Shader compile failure (%s): %s"""%(
                result,
                glGetShaderInfoLog( shader ),
            ),
            source,
            shaderType,
        )
    return shader
