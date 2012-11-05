"""Renderers are classes that encapsulate the representation of
various objects by using opengl.

"""
import numpy as np
import pyglet.gl

from pyglet.graphics.vertexbuffer import VertexBufferObject
from pyglet.gl import *

from . import colors
from .optshapes import OptSphere
from .gletools.shapes import Arrow


class AbstractRenderer(object):
    '''An AbstractRenderer is an interface for Renderers. Each
    renderer have to implement an initialization function __init__, a
    draw method to do the actual drawing and an update function, that
    is used to update the data to be displayed.

    '''
    def __init__(self, *args, **kwargs):
        pass
    
    def draw(self):
        pass
    
    def update(self, *args, **kwargs):
        pass
    
class SphereRenderer(AbstractRenderer):
    def __init__(self, atoms):
        '''This renderer represents a list of *atoms* as simple
        spheres.

        *atoms*: chemlab.Atom
        '''
        self.set_atoms(atoms)
        
    def set_atoms(self, atoms):
        self.atoms = atoms
        n_triangles = 0
        vertices = []
        normals = []
        colors_ = []
        
        for atom in atoms:
            color = colors.map.get(atom.type, colors.light_grey)
            s = OptSphere(0.4, atom.coords, color=color)
            n_triangles += s.tri_n
            vertices.append(s.tri_vertex)
            normals.append(s.tri_normals)
            colors_.append(s.tri_color)
        
        # Convert arrays to numpy arrays, float32 precision,
        # compatible with opengl, and cast to ctypes
        vertices = np.array(vertices, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        colors_ = np.array(colors_, dtype=np.uint8)

        # Store vertices, colors and normals in 3 different vertex
        # buffer objects
        self._vbo_v = VertexBufferObject(n_triangles*3*sizeof(GLfloat),
                                         GL_ARRAY_BUFFER,
                                         GL_DYNAMIC_DRAW)
        self._vbo_v.bind()
        self._vbo_v.set_data(vertices.ctypes.data_as(POINTER(GLfloat)))
        self._vbo_v.unbind()
        
        self._vbo_n = VertexBufferObject(n_triangles*3*sizeof(GLfloat),
                                         GL_ARRAY_BUFFER,
                                         GL_DYNAMIC_DRAW)
        self._vbo_n.bind()
        self._vbo_n.set_data(normals.ctypes.data_as(POINTER(GLfloat)))
        self._vbo_n.unbind()

        self._vbo_c= VertexBufferObject(n_triangles*4*sizeof(GLubyte),
                                        GL_ARRAY_BUFFER,
                                        GL_DYNAMIC_DRAW)
        self._vbo_c.bind()
        self._vbo_c.set_data(colors_.ctypes.data_as(POINTER(GLuint)))
        self._vbo_c.unbind()
        
        self._n_triangles = n_triangles
    
    def draw(self):
        # Draw all the vbo defined in set_atoms
        glEnableClientState(GL_VERTEX_ARRAY)
        self._vbo_v.bind()
        glVertexPointer(3, GL_FLOAT, 0, 0)
        
        glEnableClientState(GL_NORMAL_ARRAY)
        self._vbo_n.bind()
        glNormalPointer(GL_FLOAT, 0, 0)
        
        glEnableClientState(GL_COLOR_ARRAY)
        self._vbo_c.bind()
        glColorPointer(4, GL_UNSIGNED_BYTE, 0, 0)
        
        glDrawArrays(GL_TRIANGLES, 0, self._n_triangles)
        
        self._vbo_v.unbind()
        self._vbo_n.unbind()
        self._vbo_c.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)

    def update(self, rarray):
        offset = 0
        vertices = np.zeros(self._n_triangles*3, dtype=np.float32)
        
        for i, atom in enumerate(self.atoms):
            color = colors.map.get(atom.type, colors.light_grey)
            s = OptSphere(0.4, rarray[i], color=color)
            n = len(s.tri_vertex)
            vertices[offset:offset+n] = s.tri_vertex
            offset += n
        
        self._vbo_v.bind()
        self._vbo_v.set_data(vertices.ctypes.data_as(POINTER(GLfloat)))
        self._vbo_v.unbind()

class ForcesRenderer(AbstractRenderer):
    def __init__(self, forces, atoms):
        self.set_forces(forces, atoms)
        
    def set_forces(self, forces, atoms):
        self.forces = forces
        self.atoms = atoms
        
    def draw(self):
        for f, a in zip(self.forces, self.atoms):
            arr = Arrow(f + a.coords, a.coords)
            arr.draw()

class CubeRenderer(AbstractRenderer):
    def __init__(self, dim):
        self.dim = dim
        
    def draw(self):
        l = self.dim
        x = l*0.5 
        pyglet.graphics.draw(8*3, pyglet.gl.GL_LINES,
                             # Front Square
                       ("v3f", (x, x, x,  -x, x, x,
                                -x, x, x, -x, -x, x,
                                -x, -x, x, x, -x, x,
                                x, -x, x,  x, x, x,
                                # Back Square
                                x, x, -x,  -x, x, -x,
                                -x, x, -x, -x, -x, -x,
                                -x, -x, -x, x, -x, -x,
                                x, -x, -x,  x, x, -x,
                                # Connecting the two squares
                                x,x,x, x,x,-x,
                                -x,x,x, -x,x,-x,
                                -x,-x,x, -x,-x,-x,
                                x,-x,x, x,-x, -x)),
                             ("n3f", (0.0,)*24*3))
    
    def update(self):
        pass


class PointRenderer(AbstractRenderer):
    
    def __init__(self, sys):
        self.sys = sys
        glPointSize(10.0)
        glEnable(GL_POINT_SMOOTH)        
        self.set_atoms(self.sys.atoms)
    
    def set_atoms(self, atoms):
        self.atoms = atoms
        
        positions = []
        radii = []
        colors_ = []
        
        for atom in atoms:
            color = colors.map.get(atom.type, colors.light_grey)
            positions.append(atom.coords)
            colors_.append(color)
            radii.append(0.27)
        
        # Convert arrays to numpy arrays, float32 precision,
        # compatible with opengl, and cast to ctypes
        positions = np.array(positions, dtype=np.float32)
        radii = np.array(radii, dtype=np.float32)
        colors_ = np.array(colors_, dtype=np.uint8)

        n_points = len(positions)
        # Store vertices, colors and normals in 3 different vertex
        # buffer objects
        self._vbo_v = VertexBufferObject(n_points*3*sizeof(GLfloat),
                                         GL_ARRAY_BUFFER,
                                         GL_DYNAMIC_DRAW)
        self._vbo_v.bind()
        self._vbo_v.set_data(positions.ctypes.data_as(POINTER(GLfloat)))
        self._vbo_v.unbind()
        
        self._vbo_c= VertexBufferObject(n_points*4*sizeof(GLubyte),
                                        GL_ARRAY_BUFFER,
                                        GL_DYNAMIC_DRAW)
        self._vbo_c.bind()
        self._vbo_c.set_data(colors_.ctypes.data_as(POINTER(GLuint)))
        self._vbo_c.unbind()
        
        self._n_points = n_points
    
    def draw(self):
        # Draw all the vbo defined in set_atoms
        glEnableClientState(GL_VERTEX_ARRAY)
        self._vbo_v.bind()
        glVertexPointer(3, GL_FLOAT, 0, 0)
        
        glEnableClientState(GL_COLOR_ARRAY)
        self._vbo_c.bind()
        glColorPointer(4, GL_UNSIGNED_BYTE, 0, 0)
        
        glDrawArrays(GL_POINTS, 0, self._n_points)
        
        self._vbo_v.unbind()
        self._vbo_c.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)

    def update(self, rarray):
        positions = rarray
        
        self._vbo_v.bind()
        self._vbo_v.set_data(positions.ctypes.data_as(POINTER(GLfloat)))
        self._vbo_v.unbind()

class SphereRenderer2(AbstractRenderer):
    def __init__(self, atoms):
        self.atoms = atoms
        v_shadercode = '''
        // I should handle the perspective stuff
        // I should write some sort of normals that will be interpolated
        
        '''
        
        f_shadercode = '''
        // I should do the lighting and bitch stuff
        
        '''
    def draw(self):
        # This thing has to be done in the shaders
        return
    
    def update(self):
        pass
