'''Tests for the graphics harnessing'''
from chemlab.core import Atom, Molecule
from chemlab.graphics.qtviewer import QtViewer

from chemlab.graphics.renderers import (TriangleRenderer, SphereRenderer,
                                        AtomRenderer)

import numpy as np

def test_triangle_renderer():
    '''To see if we're able to render a triangle'''
    vertices = [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [2.0, 0.0, 0.0]]
    normals = [[0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0]]
    
    blue = [[0, 255, 255, 255]]
    colors = blue * 3
    
    v = QtViewer()
    tr = v.add_renderer(TriangleRenderer, vertices, normals, colors)
    v.run()

    
def test_sphere_renderer():
    '''To see if we can render a sphere'''
    centers = [[0.0, 0.0, 0.0]]
    radii = [[1.0]]
    colors = [[0, 255, 255, 255]]
    
    v = QtViewer()
    sr = v.add_renderer(SphereRenderer, centers, radii, colors)
    
    cr = np.array(centers)
    def update(cr=cr):
        cr[0][0] += 0.01
        sr.update_positions(cr)
        v.widget.repaint()
        
    v.schedule(update)
    
    v.run()

def test_sphere_imp_renderer():
    '''To see if we can render a sphere'''
    centers = [[0.0, 0.0, 0.0]]
    radii = [[1.0]]
    colors = [[0, 255, 255, 255]]
    
    v = QtViewer()
    sr = v.add_renderer(SphereRenderer, centers, radii, colors)
    
    cr = np.array(centers)
    def update(cr=cr):
        cr[0][0] += 0.01
        sr.update_positions(cr)
        v.widget.repaint()
        
    v.schedule(update)
    
    v.run()

def test_atom_renderer():
    '''Simple rendering of atoms as spheres'''

    mol = Molecule([Atom("O", [-0.499, 0.249, 0.0]),
                    Atom("H", [-0.402, 0.249, 0.0]),
                    Atom("H", [-0.532, 0.198, 0.10])])
    
    v = QtViewer()
    ar = v.add_renderer(AtomRenderer, mol)
    v.run()

