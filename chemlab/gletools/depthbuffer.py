# -*- coding: utf-8 -*-

"""
    :copyright: 2009 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from __future__ import with_statement

from ctypes import byref
from contextlib import nested

from .gl import *
from .util import Context

__all__ = ['DepthBuffer']

class Depthbuffer(Context):
    _get = GL_RENDERBUFFER_BINDING_EXT

    def bind(self, id):
        glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, id)
        
    def __init__(self, width, height):
        Context.__init__(self)
        id = GLuint()
        glGenRenderbuffersEXT(1, byref(id))
        self.id = id.value
        with self:
            glRenderbufferStorageEXT(GL_RENDERBUFFER_EXT, GL_DEPTH_COMPONENT, width, height)
