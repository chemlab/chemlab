from pyglet.gl import *

try:
    from pyglet.gl import GL_RGBA32F, GL_RGB16F, GL_RGB32F, GL_LUMINANCE32F
except ImportError:
    from pyglet.gl.glext_arb import (
        GL_RGBA32F_ARB as GL_RGBA32F,
        GL_RGB16F_ARB as GL_RGB16F,
        GL_RGB32F_ARB as GL_RGB32F,
        GL_LUMINANCE32F_ARB as GL_LUMINANCE32F,
    )
