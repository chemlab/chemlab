from OpenGL.GL import *
from OpenGL.raw import GL
from OpenGL.arrays import ArrayDatatype as ADT

import numpy as np

class VertexBuffer(object):

  def __init__(self, data, usage):
    self.buffer = GLuint(0)
    self.buffer = glGenBuffers(1)
    self.usage = usage
    self.data = data
    
    # Add a little warning
    if data.dtype == np.float:
      Warning('This float array is 64 bit')
    
    glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
    glBufferData(GL_ARRAY_BUFFER, ADT.arrayByteCount(data),
                 ADT.voidDataPointer(data), usage)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

  def __del__(self):
    # this causes an error otherwise
    if bool(glDeleteBuffers):
      glDeleteBuffers(1, GLuint(self.buffer))
    else:
      return

  def bind(self):
    glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
    
  def unbind(self):
    glBindBuffer(GL_ARRAY_BUFFER, 0)

  def set_data(self, data):
    self.bind()
    glBufferData(GL_ARRAY_BUFFER, ADT.arrayByteCount(data), ADT.voidDataPointer(data), self.usage)
    self.unbind()
      
  def bind_colors(self, size, type, stride=0):
    self.bind()
    glColorPointer(size, type, stride, None)

  def bind_edgeflags(self, stride=0):
    self.bind()
    glEdgeFlagPointer(stride, None)

  def bind_indexes(self, type, stride=0):
    self.bind()
    glIndexPointer(type, stride, None)

  def bind_normals(self, type, stride=0):
    self.bind()
    glNormalPointer(type, stride, None)

  def bind_texcoords(self, size, type, stride=0):
    self.bind()
    glTexCoordPointer(size, type, stride, None)

  def bind_vertexes(self, size, type, stride=0):
    self.bind()
    glVertexPointer(size, type, stride, None)
    
  def bind_attrib(self, attribute, size, type, normalized=GL_FALSE, stride=0):
    self.bind()
    glVertexAttribPointer(attribute, size, type, normalized, stride, None)