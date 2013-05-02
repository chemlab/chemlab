"""Texture data structures
"""
from OpenGL.GL import *

class Texture(object):

    def __init__(self, kind, width, height, format, dtype):
        self.kind = kind
        self.format = format
        self.id = glGenTextures(1)
        self.width, self.height = width, height
        self.dtype = dtype
        self.empty()
        
    def empty(self):
        self.bind()
        glTexImage2D(self.kind, 0, self.format, self.width, self.height, 0,
                     self.format, self.dtype, 0)
        
    def bind(self):
        glBindTexture(self.kind, self.id)

    def set_parameter(self, par, value):
        glTexParameteri(self.kind, par, value)