"""Texture data structures
"""
from OpenGL.GL import *

class Texture(object):

    def __init__(self, kind, width, height, intformat, format, dtype):
        self.kind = kind
        self.intformat = intformat
        self.format = format
        self.id = glGenTextures(1)
        self.width, self.height = width, height
        self.dtype = dtype
        self.empty()
        
    def empty(self):
        self.bind()
        glTexImage2D(self.kind, 0, self.intformat, self.width, self.height, 0,
                     self.format, self.dtype, 0)
        
    def bind(self):
        glBindTexture(self.kind, self.id)

    def set_parameter(self, par, value):
        glTexParameteri(self.kind, par, value)