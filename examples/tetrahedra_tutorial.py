import numpy as np
v1 = np.array([1.0, 0.0, -1.0/np.sqrt(2)])
v2 = np.array([-1.0, 0.0, -1.0/np.sqrt(2)])
v3 = np.array([0.0, 1.0, 1.0/np.sqrt(2)])
v4 = np.array([0.0, -1.0, 1.0/np.sqrt(2)])

from chemlab.graphics.qt import QtViewer
from chemlab.graphics.renderers import PointRenderer
from chemlab.graphics.colors import black, green, blue, red

colors = [black, green, blue, red]
v = QtViewer()
v.add_renderer(PointRenderer, np.array([v1, v2, v3, v4]), colors)

from chemlab.graphics.renderers import TriangleRenderer

vertices = np.array([
    v1, v4, v3,
    v3, v4, v2,
    v1, v3, v2,
    v2, v4, v1
])

colors = [green] * 12

# Normals: cross-product for each face
n1 = -np.cross(v4 - v1, v3 - v1)
n1 /= np.linalg.norm(n1)

n2 = -np.cross(v4 - v3, v2 - v3)
n2 /= np.linalg.norm(n2)

n3 = -np.cross(v3 - v1, v2 - v1)
n3 /= np.linalg.norm(n3)

n4 = -np.cross(v4 - v2, v1 - v2)
n4 /= np.linalg.norm(n4)

normals = [n1, n1, n1,
           n2, n2, n2,
           n3, n3, n3,
           n4, n4, n4]

#v.add_renderer(TriangleRenderer, vertices, normals, colors)
from chemlab.graphics.renderers import AbstractRenderer

class TetrahedraRenderer(AbstractRenderer):
    def __init__(self, widget, positions):
        super(TetrahedraRenderer, self).__init__(widget)
        
        v1 = np.array([1.0, 0.0, -1.0/np.sqrt(2)])
        v2 = np.array([-1.0, 0.0, -1.0/np.sqrt(2)])
        v3 = np.array([0.0, 1.0, 1.0/np.sqrt(2)])
        v4 = np.array([0.0, -1.0, 1.0/np.sqrt(2)])

        positions = np.array(positions)
        
        # Vertices of a single tetrahedra
        self._th_vertices = np.array([
            v1, v4, v3,
            v3, v4, v2,
            v1, v3, v2,
            v2, v4, v1
        ])
        
        self._th_normals = np.array([
            n1, n1, n1,
            n2, n2, n2,
            n3, n3, n3,
            n4, n4, n4])
        
        self.n_tetra = len(positions)
        
        tot_vertices = []
        for pos in positions:
            tot_vertices.extend(self._th_vertices + pos)
        
        tot_normals = np.tile(self._th_normals, (self.n_tetra, 1))
        tot_colors = [green] * self.n_tetra * 12
        
        self.tr = TriangleRenderer(widget, tot_vertices,
                                  tot_normals, tot_colors)
        
    def draw(self):
        self.tr.draw()

positions = []

for x in range(5):
    for y in range(5):
        for z in range(5):
            positions.append([float(x)*2, float(y)*2, float(z)*2])

v.add_renderer(TetrahedraRenderer, positions)
v.widget.camera.position = np.array([0.0, 0.0, 20.0])
v.run()
