# -*- coding: utf-8 -*-

"""
    :copyright: 2009 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from __future__ import with_statement

from ctypes import c_char_p, pointer, cast, byref, c_char, create_string_buffer, c_float
import numpy as np

from .gl import *
from .util import Context

__all__ = 'VertexShader', 'FragmentShader', 'ShaderProgram'

class GLObject(object):
    _del = glDeleteObjectARB
    class Exception(Exception): pass

    def log(self):
        length = c_int(0)
        glGetObjectParameterivARB(self.id, GL_OBJECT_INFO_LOG_LENGTH_ARB, byref(length))
        log = create_string_buffer(length.value)
        glGetInfoLogARB(self.id, length.value, None, log)
        return log.value
    
    def __del__(self):
        self._del(self.id)

class Shader(GLObject):
    
    def __init__(self, source):
        if not gl_info.have_extension(self.ext):
            raise self.Exception('%s extension is not available' % self.ext)
        self.id = glCreateShaderObjectARB(self.type)
        self.source = source
        ptr = cast(c_char_p(source), POINTER(c_char))
        glShaderSourceARB(self.id, 1, byref(ptr), None)

        glCompileShader(self.id)
        
        status = c_int(0)
        glGetObjectParameterivARB(self.id, GL_OBJECT_COMPILE_STATUS_ARB, byref(status))
        if status.value == 0:
            error = self.log()
            raise self.Exception('failed to compile:\n%s' % error)
    
    @classmethod
    def open(cls, name):
        source = open(name).read()
        return cls(source)

class VertexShader(Shader):
    type = GL_VERTEX_SHADER_ARB
    ext = 'GL_ARB_vertex_program'

class FragmentShader(Shader):
    type = GL_FRAGMENT_SHADER_ARB
    ext = 'GL_ARB_fragment_program'

class Variable(object):
    def set(self, program, name):
        with program:
            location = program.uniform_location(name)
            if location != -1:
                self.do_set(location)

class Sampler2D(Variable):
    def __init__(self, unit):
        self.value = unit - GL_TEXTURE0

    def do_set(self, location):
        glUniform1i(location, self.value)

typemap = {
    float:{
        1:glUniform1f,
        2:glUniform2f,
        3:glUniform3f,
        16:glUniform4f,
    },
    int:{
        1:glUniform1i,
        2:glUniform2i,
        3:glUniform3i,
    },
    np.dtype("float"): {
        1:glUniform1f,
        2:glUniform2f,
        3:glUniform3f,
        4:glUniform4f,
    },
    np.dtype("float64"): {
        1:glUniform1f,
        2:glUniform2f,
        3:glUniform3f,
        4:glUniform4f,
    }
}

typemap_mat = {
    np.dtype("float"): {
        2: glUniformMatrix2fv,
        3: glUniformMatrix3fv,
        4: glUniformMatrix4fv,
    },
    np.dtype("float64"): {
        2: glUniformMatrix2fv,
        3: glUniformMatrix3fv,
        4: glUniformMatrix4fv,
    }
}

class Vars(object):
    def __init__(self, program):
        self.__dict__['_program'] = program

    def __setattr__(self, name, value):
        # I think we should get like numpy stuff
        if isinstance(value, np.ndarray):
            # Let's handle vec[1-4]
            if len(value.shape) == 1 and 1 < value.shape[0] <= 4:
                setter = typemap[value.dtype][value.shape[0]]
                self._set_array(setter, name, value)
            # Let's handle mat[2-4]
            elif (len(value.shape) == 2 and
                value.shape[0] == value.shape[1] and
                1 < value.shape[0] <= 4):
                setter = typemap_mat[value.dtype][value.shape[0]]
                self._set_matrix(setter, name, value)
        
        elif isinstance(value, (list, tuple)):
            setter = typemap[type(value[0])][len(value)]
            self._set_array(setter, name, value)
                
        elif isinstance(value, (int, float)): 
            setter = typemap[type(value)][1]
            self._set_number(setter, name, value)
        else:
            raise Exception("Type %s not supported" % str(type(value)))
        
    def _set_matrix(self, setter, name, value):
        '''Set the matrix as attribute to the program'''
        with self._program:
            location = self._program.uniform_location(name)
            if location != -1:
                setter(location, 1, GL_FALSE, np_to_ctypes(value))

    def _set_array(self, setter, name, value):
        '''Set the array as an attribute to the program'''
        with self._program:
            location = self._program.uniform_location(name)
            if location != -1:
                setter(location, *value)
    
    def _set_number(self, setter, name, value):
        with self._program:
            location = self._program.uniform_location(name)
            if location != -1:
                setter(location, value)

class Attr(object):
    def __init__(self, program):
        self.__dict__['_program'] = program

    def __setattr__(self, name, value):
        with self._program:
            location = self._program.uniform_location(name)
            if location != -1:
                setter(location, value)
    
class ShaderProgram(GLObject, Context):
    _get = GL_CURRENT_PROGRAM
    
    def bind(self, id):
        glUseProgram(id)

    def __init__(self, *shaders, **variables):
        Context.__init__(self)
        self.id = glCreateProgramObjectARB()
        self.shaders = list(shaders)
        for shader in shaders:
            glAttachObjectARB(self.id, shader.id)

        self.link()

        self.vars = Vars(self)
        for name, value in variables.items():
            setattr(self.vars, name, value)

    def link(self):
        glLinkProgramARB(self.id)
       
        status = c_int(0)
        glGetObjectParameterivARB(self.id, GL_OBJECT_LINK_STATUS_ARB, byref(status))
        if status.value == 0:
            error = self.log()
            raise self.Exception('failed to link:\n%s' % error)

        glValidateProgram(self.id)
        glGetObjectParameterivARB(self.id, GL_VALIDATE_STATUS, byref(status))
        if status.value == 0:
            error = self.log()
            raise self.Exception('failed to validate:\n%s' % error)

    def uniform_location(self, name):
        return glGetUniformLocation(self.id, name)

    def attrib_location(self, name):
        location = 4
        glBindAttribLocation(self.id, location, name)
        return location

def np_to_ctypes(array):
    if issubclass(array.dtype.type, float):
        basetype = c_float
    else:
        raise Exception("Cannot convert array of type: " + str(array.dtype.type))
    # Linear array
    if len(array.shape) == 1:
        return (basetype * len(array))(*array)
    # Matrix
    elif len(array.shape) == 2:
        array2 = np.asarray(array).ravel('F') # Column-major
        return (basetype * len(array2))(*array2)
    else:
        raise Exception("Passed array not valid")
