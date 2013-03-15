'''Tests for the graphics harnessing'''
from chemlab.core import Atom, Molecule
from chemlab.graphics.qtviewer import QtViewer
from chemlab.graphics.colors import orange, blue, forest_green
from chemlab.graphics.renderers import (TriangleRenderer, SphereRenderer,
                                        SphereImpostorRenderer, PointRenderer,
                                        AtomRenderer, BoxRenderer, LineRenderer)

from chemlab.graphics.uis import TextUI
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

def test_point_renderer():
    '''To see if we're able to render a triangle'''
    vertices = [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [2.0, 0.0, 0.0]]
    blue = [[0, 255, 255, 255]]
    
    colors = blue * 3
    
    v = QtViewer()
    tr = v.add_renderer(PointRenderer, vertices, colors)
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
    centers = [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]]
    radii = [0.5, 0.1, 0.5]
    colors = [orange, blue, forest_green]

    v = QtViewer()
    sr = v.add_renderer(SphereImpostorRenderer, centers, radii, colors)
    
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

def test_box_renderer():
    vectors = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    v = QtViewer()
    ar = v.add_renderer(BoxRenderer, vectors)
    v.run()

def test_line_renderer():
    vectors = np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0],
                        [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    colors = [blue, orange, orange, orange]
    
    v = QtViewer()
    ar = v.add_renderer(LineRenderer, vectors, colors)
    v.run()

    
def test_text_ui():
    v = QtViewer()
    mol = Molecule([Atom("O", [-0.499, 0.249, 0.0]),
                    Atom("H", [-0.402, 0.249, 0.0]),
                    Atom("H", [-0.532, 0.198, 0.10])])
    
    # To add some interaction to it
    ar = v.add_renderer(AtomRenderer, mol, "impostors")
    tr = v.add_ui(TextUI, 100, 100, 'Hello guys')
    
    v.run()
    
    
def test_unproject():
    v = QtViewer()
    
    vectors = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    colors = [blue, blue]
    ar = v.add_renderer(LineRenderer, vectors, colors)

    def mouse_move(evt):
        x,y =  evt.x(), evt.y()
        w = v.widget.width()
        h = v.widget.height()
        x, y = 2*float(x)/w - 1.0, 1.0 - 2*float(y)/h
        
        start =  v.widget.camera.unproject(x,y,-1.0)
        print x,y, 0.0
        print start
        vectors[1] = [0.0, 0.0, 0.0]
        vectors[0] = start
        
        ar.update_positions(np.array(vectors))
        v.widget.repaint()
    v.mousePressEvent = mouse_move # Super Hack
    v.run()
    
# TODO: cleanup This test doesn't work...
def test_arcball():
    v = QtViewer()
    
    mol = Molecule([Atom("O", [-0.499, 0.249, 0.0]),
                    Atom("H", [-0.402, 0.249, 0.0]),
                    Atom("H", [-0.532, 0.198, 0.10])])
    
    ar = v.add_renderer(AtomRenderer, mol)

    
    vectors = [[0.0, 0.0, 0.0]]*4
    colors = [blue]*4

    ln = v.add_renderer(LineRenderer, vectors, colors)
    
    def mouse_move(evt):
        cam = v.widget.camera
        
        pos = v._last_mouse_pos
        x,y =  pos.x(), pos.y()
        
        pos = evt.pos()
        v._last_mouse_pos  = pos
        x2, y2 = pos.x(), pos.y()
        
        w = v.widget.width()
        h = v.widget.height()
        x, y = 2*float(x)/w - 1.0, 1.0 - 2*float(y)/h
        
        x2, y2 = 2*float(x2)/w - 1.0, 1.0 - 2*float(y2)/h
        

        cam.arcball_rotation(x, y, x2-x, y2-y)
        
        start = map_to_arcball(x,y)
        end = map_to_arcball(x2, y2)

        start = cam.unproject(start[0], start[1], -start[2])
        end = cam.unproject(end[0], end[1], -end[2])
        
        vectors[1] = start
        vectors[3] = end
        
        ln.update_positions(vectors)
        
        v.widget.repaint()
        
    
    from chemlab.graphics.camera import map_to_arcball        
    
    v.mouseMoveEvent = mouse_move # Super Hack
    v.run()