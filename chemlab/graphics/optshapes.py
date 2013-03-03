from .gletools.shapes import Sphere
from . import colors
import numpy as np
import pyglet

_SPHERE_MRES = Sphere(1.0, np.array([0.0, 0.0, 0.0]), parallels=10, meridians=15)

# Unit Sphere

class OptSphere:

    def __init__(self, radius, position, res="med", color=colors.light_grey):

        olddim = len(_SPHERE_MRES.tri_vertex)
        vertex = _SPHERE_MRES.tri_vertex.reshape((olddim/3, 3))
        
        self.tri_vertex = vertex * radius + position
        self.tri_vertex = self.tri_vertex.reshape(olddim)
        
        _SPHERE_MRES.tri_vertex.reshape(olddim)
        self.tri_normals = _SPHERE_MRES.tri_normals.copy()
        self.tri_color = color * (olddim/3)

        self.tri_n = olddim/3
        
    def draw(self):
        self.vertex_list.draw(pyglet.gl.GL_TRIANGLES)

        

