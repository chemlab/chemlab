"""Texture data structures
"""
from __future__ import print_function

import numpy as np
from OpenGL.GL import *

class Texture(object):

    def __init__(self, kind, width, height, intformat,
                 format, dtype, data=None):
        self.kind = kind
        self.intformat = intformat
        self.format = format
        self.id = int(glGenTextures(1)) # Avoid returning a numpy array
        self.width, self.height = width, height
        self.dtype = dtype
        self.data = data
        self.empty()

    def empty(self):
        self.bind()
        glTexImage2D(self.kind, 0, self.intformat, self.width, self.height, 0,
                     self.format, self.dtype, self.data)
    def bind(self):
        glBindTexture(self.kind, self.id)

    def set_parameter(self, par, value):
        glTexParameteri(self.kind, par, value)

    def delete(self):
        glDeleteTextures(1, np.array(self.id))
