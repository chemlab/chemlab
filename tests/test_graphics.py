'''Tests for the graphics harnessing'''
from chemlab.core import Atom, Molecule
from chemlab.graphics.qtviewer import QtViewer
from chemlab.graphics.colors import orange, blue, forest_green
from chemlab.graphics.renderers import (TriangleRenderer, SphereRenderer,
                                        SphereImpostorRenderer, PointRenderer,
                                        AtomRenderer, BoxRenderer, LineRenderer,
                                        CylinderRenderer, BondRenderer, BallAndStickRenderer,
                                        WireframeRenderer)
from chemlab.graphics.colors import green, white, black, blue, purple, red
from chemlab.graphics.uis import TextUI
import numpy as np
import time

from chemlab.graphics.qttrajectory import QtTrajectoryViewer, format_time

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

def test_point_fog():
    '''To see if we're able to render a triangle'''

    NPOINTS = 10000
    vertices = (np.random.random((NPOINTS, 3))-0.5)*3
    #vertices = [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [2.0, 0.0, 0.0]]
    blue = [[0, 255, 0, 125]]
    
    colors = blue * NPOINTS
    
    v = QtViewer()

    tr = v.add_renderer(PointRenderer, vertices, colors)
    v.run()

    
def test_sphere_renderer():
    '''To see if we can render a sphere'''

    centers = [[0.0, 0.0, 0.0]]
    radii = [[1.0]]
    colors = [[0, 255, 255, 125]]
    
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
    colors = np.array([orange, blue, forest_green])
    
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
    ar = v.add_renderer(AtomRenderer, mol.r_array, mol.type_array)
    v.run()

def test_box_renderer():
    vectors = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    v = QtViewer()
    ar = v.add_renderer(BoxRenderer, vectors, origin=np.array([-0.5, -0.5, -0.5]))
    v.run()

def test_line_renderer():
    vectors = np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0],
                        [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    colors = [blue, orange, orange, orange]
    
    v = QtViewer()
    ar = v.add_renderer(LineRenderer, vectors, colors)
    v.run()

    
def test_cylinder_renderer():
    bounds = np.array([[[-1.0, 0.0, 0.0], [-1.0, 1.0, 0.0]],
                       [[1.0, 0.0, 0.0], [1.0, 3.0, 0.0]],
                       [[1.0, 0.0, 0.0], [1.0, 0.0, 1.0]]])
    radii = np.array([0.5, 0.3, 0.3])
    colors = np.array([blue, orange, green])
    
    # Test for speed
    # random bounds
    # n = 1000
    #bounds = np.random.rand(n, 2, 3) * 10
    #radii = np.random.rand(n)
    #colors = np.array([blue] * n)
    
    v = QtViewer()
    import time
    t0 = time.time()
    ar = v.add_renderer(CylinderRenderer, bounds, radii, colors)
    print time.time() - t0
    
    #ar.update_bounds(bounds)
    
    v.run()
    
def test_bond_renderer():

    from chemlab.db.cirdb import CirDB
    from collections import defaultdict
    
    v = QtViewer()
    v.widget.background_color = black
    mol = Molecule([Atom("O", [-0.499, 0.249, 0.0]),
                    Atom("H", [-0.402, 0.249, 0.0]),
                    Atom("H", [-0.532, 0.198, 0.10])])
    
    mol.bonds = np.array([[0, 1],[0, 2]])
    
    
    mol = CirDB().get("molecule", "moronic acid")
    #radii_map = {"O": 0.03, "H": 0.03}
    radii_map = defaultdict(lambda: 0.03)
    
    br = v.add_renderer(BondRenderer, mol.bonds, mol.r_array,
                        mol.type_array, style='lines')
    ar = v.add_renderer(AtomRenderer, mol.r_array, mol.type_array,
                        "impostors", radii_map = radii_map)
    
    v.run()
    

def test_ball_and_stick_renderer():
    from collections import defaultdict
    from chemlab.db.cirdb import CirDB
    
    v = QtViewer()
    v.widget.background_color = black
    mol = Molecule([Atom("O", [-0.499, 0.249, 0.0]),
                    Atom("H", [-0.402, 0.249, 0.0]),
                    Atom("H", [-0.532, 0.198, 0.10])])
    
    mol.bonds = np.array([[0, 1],[0, 2]])
    
    mol = CirDB().get("molecule", "moronic acid")
    ar = v.add_renderer(BallAndStickRenderer, mol.r_array, mol.type_array, mol.bonds)
    
    # Try without bonds
    ar2 = v.add_renderer(BallAndStickRenderer, mol.r_array + 0.5, mol.type_array, np.array([]))
    
    v.run()

def test_wireframe_renderer():
    from collections import defaultdict
    from chemlab.db.cirdb import CirDB
    
    v = QtViewer()
    v.widget.background_color = black
    mol = Molecule([Atom("O", [-0.499, 0.249, 0.0]),
                    Atom("H", [-0.402, 0.249, 0.0]),
                    Atom("H", [-0.532, 0.198, 0.10])])
    
    mol.bonds = np.array([[0, 1],[0, 2]])
    
    mol = CirDB().get("molecule", "moronic acid")
    ar = v.add_renderer(WireframeRenderer, mol.r_array, mol.type_array, mol.bonds)
    
    # Try without bonds
    #ar2 = v.add_renderer(WireframeRenderer, mol.r_array + 0.5, mol.type_array, np.array([]))
    
    v.run()


def test_text_ui():
    v = QtViewer()
    mol = Molecule([Atom("O", [-0.499, 0.249, 0.0]),
                    Atom("H", [-0.402, 0.249, 0.0]),
                    Atom("H", [-0.532, 0.198, 0.10])])
    
    # To add some interaction to it
    ar = v.add_renderer(AtomRenderer, mol.r_array, mol.type_array, "impostors")
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
    
def test_traj_viewer():
    from chemlab.io import datafile
    tv = QtTrajectoryViewer()
    
    s = datafile('tests/data/water.gro').read('system')
    ar = tv.add_renderer(AtomRenderer, s.r_array, s.type_array)

    times, frames = datafile('tests/data/trajout.xtc').read('trajectory')
    tv.set_ticks(len(frames))
    
    @tv.update_function
    def update(index):
        f = frames[index]
        ar.update_positions(f)
        tv.set_text(format_time(times[index]))
        tv.widget.repaint()
    
    tv.run()

def test_camera_autozoom():
    v = QtViewer()
    mol = Molecule([Atom("O", [-0.499, 0.249, 0.0]),
                    Atom("H", [-0.402, 0.249, 0.0]),
                    Atom("H", [-0.532, 0.198, 0.10])])
    from chemlab.io import datafile
    s = datafile('tests/data/3ZJE.pdb').read('system')
    
    # To add some interaction to it
    ar = v.add_renderer(AtomRenderer, s.r_array, s.type_array, "impostors")
    v.widget.camera.autozoom(s.r_array)
    
    v.run()

def test_noeffect():
    from chemlab.graphics.postprocessing import NoEffect
    v = QtViewer()
    centers = [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]]
    radii = [0.5, 0.1, 0.5]
    colors = np.array([orange, blue, forest_green])
    
    sr = v.add_renderer(SphereImpostorRenderer, centers, radii, colors)
    
    v.widget.post_processing = NoEffect(v.widget)
    
    v.run()

def test_fxaa():
    from chemlab.graphics.postprocessing.fxaa import FXAAEffect
    v = QtViewer()
    centers = [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]]
    radii = [0.5, 0.1, 0.5]
    colors = np.array([orange, blue, forest_green])
    
    sr = v.add_renderer(SphereImpostorRenderer, centers, radii, colors)
    
    v.widget.post_processing = FXAAEffect(v.widget)
    
    v.run()
    
def test_ssao():
    from chemlab.graphics.postprocessing.ssao import SSAOEffect
    from chemlab.db import ChemlabDB
    from chemlab.io import datafile
    
    cdb = ChemlabDB()
    
    # mol = cdb.get('molecule', 'example.norbornene')
    
    mol = datafile('tests/data/3ZJE.pdb').read('system')
    v = QtViewer()
    
    sr = v.add_renderer(AtomRenderer, mol.r_array, mol.type_array, 'polygons')
    
    #sr = sr.sr
    #sr.FRAGMENT_SHADER = open('chemlab/graphics/renderers/shaders/sphereimp_writenormal.frag').read()
    #sr.compile_shader()
    
    v.widget.post_processing = SSAOEffect(v.widget)
    
    v.run()
