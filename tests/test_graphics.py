'''Tests for the graphics harnessing'''
import time
import numpy as np
from collections import defaultdict

from chemlab.core import Atom, Molecule
from chemlab.graphics.qtviewer import QtViewer
from chemlab.graphics import colors

from chemlab.graphics.renderers import (TriangleRenderer, SphereRenderer,
                                        SphereImpostorRenderer, PointRenderer,
                                        AtomRenderer, BoxRenderer, LineRenderer,
                                        CylinderRenderer, BondRenderer, BallAndStickRenderer,
                                        WireframeRenderer, CylinderImpostorRenderer)

from chemlab.graphics.uis import TextUI

from chemlab.db import ChemlabDB, CirDB
from chemlab.io import datafile

from chemlab.graphics.qttrajectory import QtTrajectoryViewer, format_time
from chemlab.graphics.postprocessing import (SSAOEffect,
                                             FXAAEffect,
                                             GammaCorrectionEffect,
                                             OutlineEffect, GlowEffect, NoEffect)

cdb = ChemlabDB()

    
def test_triangle_renderer():
    '''To see if we're able to render a triangle'''
    vertices = [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [2.0, 0.0, 0.0]]
    normals = [[0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0]]
    colors = [colors.blue]* 3

    v = QtViewer()
    tr = v.add_renderer(TriangleRenderer, vertices, normals, colors, shading='toon')
    v.run()

def test_point_renderer():
    '''To see if we're able to render a triangle'''
    vertices = [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [2.0, 0.0, 0.0]]
    colors = [colors.blue] * 3

    v = QtViewer()
    tr = v.add_renderer(PointRenderer, vertices, colors)
    v.run()

def test_point_fog():
    '''To see if we're able to render a triangle'''

    NPOINTS = 10000
    vertices = (np.random.random((NPOINTS, 3))-0.5)*3
    colors = [colors.blue] * NPOINTS

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
    colors = np.array([colors.orange, colors.blue, colors.forest_green])

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
    colors = [colors.blue, colors.orange, colors.orange, colors.orange]

    v = QtViewer()
    ar = v.add_renderer(LineRenderer, vectors, colors)
    v.run()


def test_cylinder_renderer():
    bounds = np.array([[[-1.0, 0.0, 0.0], [-1.0, 1.0, 0.0]],
                       [[1.0, 0.0, 0.0], [1.0, 3.0, 0.0]],
                       [[1.0, 0.0, 0.0], [1.0, 0.0, 1.0]]])
    radii = np.array([0.5, 0.3, 0.3])
    colors = np.array([colors.blue, colors.orange, colors.green])

    # Test for speed
    # random bounds
    # n = 1000
    #bounds = np.random.rand(n, 2, 3) * 10
    #radii = np.random.rand(n)
    #colors = np.array([blue] * n)

    v = QtViewer()
    t0 = time.time()
    ar = v.add_renderer(CylinderRenderer, bounds, radii, colors)
    print(time.time() - t0)

    #ar.update_bounds(bounds)

    v.run()

def test_cylinder_impostor_renderer():
    bounds = np.array([[[-1.0, 0.0, 0.0], [-1.0, 1.0, 0.0]],
                       [[1.0, 0.0, 0.0], [1.0, 3.0, 0.0]],
                       [[1.0, 0.0, 0.0], [1.0, 0.0, 1.0]]])
    radii = np.array([0.5, 0.3, 0.3])
    colors = np.array([colors.blue, colors.orange, colors.green])

    bounds = np.array([[[0.0, 0.0, 0.0], [0.0, 1.0, 0.0]]])
    radii = np.array([0.2])
    colors = np.array([colors.blue])

    # Test for speed
    # random bounds
    #n = 50000
    #bounds = np.random.rand(n, 2, 3) * 10
    #radii = np.random.rand(n)/10.0
    #colors = np.array([colors.blue] * n)

    v = QtViewer()
    ar = v.add_renderer(CylinderImpostorRenderer, bounds, radii, colors)    
    sr = v.add_renderer(SphereImpostorRenderer, bounds[:, 0], radii, colors)
    sr = v.add_renderer(SphereImpostorRenderer, bounds[:, 1], radii, colors)
    v.run()
    
    # Test updates
    ar.update_radii([0.1])
    bounds[0,0] -= 1.0
    ar.update_bounds(bounds)
    ar.update_colors([colors.green])
    v.run()
    
    # Test emptiness
    ar.change_attributes([], [], [])


def test_bond_renderer():
    v = QtViewer()
    v.widget.background_color = colors.black
    mol = Molecule([Atom("O", [-0.499, 0.249, 0.0]),
                    Atom("H", [-0.402, 0.249, 0.0]),
                    Atom("H", [-0.532, 0.198, 0.10])])

    mol.bonds = np.array([[0, 1],[0, 2]])


    #mol = CirDB().get("molecule", "moronic acid")
    #radii_map = {"O": 0.03, "H": 0.03}
    radii_map = defaultdict(lambda: 0.03)

    br = v.add_renderer(BondRenderer, mol.bonds, mol.r_array,
                        mol.type_array, style='impostors')
    ar = v.add_renderer(AtomRenderer, mol.r_array, mol.type_array,
                        "impostors", radii_map = radii_map)

    v.run()


def test_ball_and_stick_renderer():


    v = QtViewer()
    v.add_post_processing(SSAOEffect, kernel_radius = 0.15)
    
    mol = datafile('tests/data/3ZJE.pdb').read('molecule')
    mol.bonds = find_bonds(mol)

    ar = v.add_renderer(BallAndStickRenderer, mol.r_array, mol.type_array, mol.bonds)
    # ar2 = v.add_renderer(BallAndStickRenderer, mol.r_array + 0.5, mol.type_array, np.array([]))

    v.run()

def test_wireframe_renderer():
    v = QtViewer()
    #v.widget.background_color = black
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
    colors = [colors.blue, colors.blue]
    ar = v.add_renderer(LineRenderer, vectors, colors)

    def mouse_move(evt):
        x,y =  evt.x(), evt.y()
        w = v.widget.width()
        h = v.widget.height()
        x, y = 2*float(x)/w - 1.0, 1.0 - 2*float(y)/h

        start =  v.widget.camera.unproject(x,y,-1.0)
        print(x,y, 0.0)
        print(start)
        vectors[1] = [0.0, 0.0, 0.0]
        vectors[0] = start

        ar.update_positions(np.array(vectors))
        v.widget.repaint()
    v.mousePressEvent = mouse_move # Super Hack
    v.run()

def find_bonds(sys):
    from chemlab.libs.ckdtree import cKDTree
    ck = cKDTree(sys.r_array)
    return np.unique(ck.query_pairs(0.15))


def test_traj_viewer():
    tv = QtTrajectoryViewer()

    s = datafile('tests/data/water.gro').read('system')
    #ar = tv.add_renderer(WireframeRenderer, s.r_array, s.type_array, find_bonds(s))
    ar = tv.add_renderer(BallAndStickRenderer, s.r_array, s.type_array, find_bonds(s))

    times, frames = datafile('tests/data/trajout.xtc').read('trajectory')
    tv.set_ticks(len(frames))

    @tv.update_function
    def update(index):
        f = frames[index]
        ar.update_positions(f)
        tv.set_text(format_time(times[index]))
        tv.widget.update()

    tv.run()

def test_camera_autozoom():
    v = QtViewer()
    mol = Molecule([Atom("O", [-0.499, 0.249, 0.0]),
                    Atom("H", [-0.402, 0.249, 0.0]),
                    Atom("H", [-0.532, 0.198, 0.10])])
    
    s = datafile('tests/data/3ZJE.pdb').read('system')

    # To add some interaction to it
    ar = v.add_renderer(AtomRenderer, s.r_array, s.type_array, "impostors")
    v.widget.camera.autozoom(s.r_array)

    v.run()

def test_noeffect():
    v = QtViewer()
    centers = [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]]
    radii = [0.5, 0.1, 0.5]
    colors_ = np.array([colors.orange, colors.blue, colors.forest_green])

    sr = v.add_renderer(SphereImpostorRenderer, centers, radii, colors_)

    v.widget.post_processing.append(NoEffect(v.widget))

    v.run()

def test_fxaa():
    centers = [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]]
    radii = [0.5, 0.1, 0.5]
    colors_ = np.array([colors.orange, colors.blue, colors.forest_green])


    vectors = np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0],
                        [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    colors_ = [colors.blue, colors.orange, colors.orange, colors.orange]

    v = QtViewer()
    ar = v.add_renderer(LineRenderer, vectors, colors_)

    #sr = v.add_renderer(SphereImpostorRenderer, centers, radii, colors)

    v.widget.post_processing.append(FXAAEffect(v.widget, span_max=8.0,
                                               reduce_mul=1/8.0,
                                               reduce_min=1/128.0))
    v.run()

def test_ssao():
    cdb = ChemlabDB()
    mol = datafile('tests/data/3ZJE.pdb').read('system')
    v = QtViewer()

    v.widget.camera.autozoom(mol.r_array)
    v.widget.post_processing.append(SSAOEffect(v.widget, kernel_size=16,
                                               kernel_radius=3.0, ssao_power=2.7))
    sr = v.add_renderer(AtomRenderer, mol.r_array, mol.type_array, 'impostors')
    #ar = v.add_renderer(BallAndStickRenderer, mol.r_array, mol.type_array, [])
    v.widget.camera.orbit_y(90)

    v.run()


def test_gamma():
    cdb = ChemlabDB()

    mol = datafile('tests/data/3ZJE.pdb').read('system')
    v = QtViewer()

    v.widget.camera.autozoom(mol.r_array)
    v.widget.camera.orbit_y(3.14/3)
    sr = v.add_renderer(AtomRenderer, mol.r_array, mol.type_array,
                        'impostors', shading='phong')

    v.add_post_processing(SSAOEffect, ssao_power=4.0)
    v.add_post_processing(GammaCorrectionEffect)
    v.run()

def test_outline():

    mol = cdb.get('molecule', 'example.norbornene')

    mol = datafile('tests/data/3ZJE.pdb').read('system')
    #mol = datafile('tests/data/water.gro').read('system')
    #mol = datafile('tests/data/benzene.mol').read('molecule')
    v = QtViewer()

    v.widget.camera.autozoom(mol.r_array)
    sr = v.add_renderer(AtomRenderer, mol.r_array, mol.type_array,
                        'impostors', shading='toon')

    v.add_post_processing(OutlineEffect, 'depthnormal')
    v.add_post_processing(SSAOEffect, ssao_power=4.0)
    v.add_post_processing(FXAAEffect)
    v.add_post_processing(GammaCorrectionEffect)
    v.run()

def test_glow():
    from PySide import QtCore
    
    cdb = ChemlabDB()
    mol = cdb.get('molecule', 'example.norbornene')
    
    v = QtViewer()
    colors = np.array([(255, 0, 0, 255)]*mol.n_atoms)
    colors[0][3] = 0

    v.widget.camera.autozoom(mol.r_array)
    sr = v.add_renderer(SphereImpostorRenderer, mol.r_array, [0.1]*mol.n_atoms,
                        colors)

    ge = v.add_post_processing(GlowEffect)
    #v.add_post_processing(GammaCorrectionEffect)
    def changeglow():
        #ge.radius = np.sin(time.time()*10.0) + 2.5
        colors[0][3] = 255 * (np.sin(time.time()*10.0)*0.5 + 0.5)
        sr.update_colors(colors)
        v.widget.update()

    timer = QtCore.QTimer()
    timer.timeout.connect(changeglow)
    timer.start(10)
    v.run()

from OpenGL.GL import *

import os

def test_offline():
    # Api for PNG saving
    v = QtViewer()
    mol = cdb.get('molecule', 'example.norbornene')
    sr = v.add_renderer(AtomRenderer, mol.r_array, mol.type_array, 'impostors', shading='toon')
    v.add_post_processing(SSAOEffect, kernel_size=128)
    v.add_post_processing(FXAAEffect)
    ne = v.add_post_processing(NoEffect)
    
    v.widget.camera.autozoom(mol.r_array)
    
    def dump():
        image = v.widget.toimage(2048, 2048)
        image.save("/tmp/hello.png")
        os.system("eog /tmp/hello.png")        
        
    from PySide.QtCore import Qt
    v.key_actions[Qt.Key_A] = dump
    
    v.run()
    

def test_multiple_post_processing():
    v = QtViewer()
    cdb = ChemlabDB()
    mol = cdb.get('molecule', 'example.norbornene')
    #mol = datafile('/home/gabriele/projects/LiCl/interface/loafintjc-heat/equilibrium.gro').read('system')
    sr = v.add_renderer(AtomRenderer, mol.r_array, mol.type_array, 'impostors', shading='toon')

    # Adding multiple post processing effects


    v.add_post_processing(SSAOEffect)
    v.add_post_processing(GammaCorrectionEffect, 2.0)
    #v.add_post_processing(GammaCorrectionEffect, 2.0)
    #v.add_post_processing(FXAAEffect)

    v.run()


def test_pickers():
    from chemlab.graphics.pickers import SpherePicker, CylinderPicker
    from chemlab.core.molecule import guess_bonds
    #mol = datafile('tests/data/benzene.mol').read('molecule')
    mol = ChemlabDB().get('molecule', 'example.water')

    centers = mol.r_array
    radii = np.array([0.05]*mol.n_atoms)
    colors = np.array([[0, 255, 255, 255]]*mol.n_atoms)
    bounds = mol.r_array.take(mol.bonds, axis=0)

    b_radii = np.array([0.05]*mol.n_bonds)
    b_colors = np.array([[0, 255, 255, 255]]*mol.n_bonds)

    v = QtViewer()
    #v.widget.camera.autozoom(mol.r_array)
    sr = v.add_renderer(SphereImpostorRenderer, centers, radii*1.2, colors, transparent=False)
    cr = v.add_renderer(CylinderImpostorRenderer, bounds, b_radii, b_colors)

    sp = SpherePicker(v.widget, centers, radii*1.2)
    cp = CylinderPicker(v.widget, bounds, b_radii)

    def on_click(evt):
        x, y = v.widget.screen_to_normalized(evt.x(), evt.y())
        a_i, a_d = sp.pick(x, y)
        b_i, b_d = cp.pick(x, y)
        print('A', a_d)
        print('B', b_d)

    v.widget.clicked.connect(on_click)

    v.run()

def test_toon_shading():
    from chemlab.core.molecule import guess_bonds

    cdb = ChemlabDB()

    #mol = cdb.get('molecule', 'example.norbornene')

    mol = datafile('tests/data/3ZJE.pdb').read('system')
    v = QtViewer()
    #v.widget.post_processing = FXAAEffect(v.widget)
    #v.widget.post_processing = SSAOEffect(v.widget, kernel_size=64, kernel_radius=1.0, ssao_power=2.0)


    v.widget.camera.autozoom(mol.r_array)
    #sr = v.add_renderer(AtomRenderer, mol.r_array,
    #                    mol.type_array, 'impostors',
    #                    shading='toon')
    #sr = v.add_renderer(AtomRenderer, mol.r_array,
    #                    mol.type_array, 'polygons',
    #                    shading='toon')

    ar = v.add_renderer(BallAndStickRenderer,
                        mol.r_array, mol.type_array,
                        guess_bonds(mol.r_array, mol.type_array),
                        shading='toon')

    v.run()


# Tests for the molecular viewer
def test_molecular_viewer():
    from chemlab.graphics.qtmolecularviewer import QtMolecularViewer
    cdb = ChemlabDB()

    mol = cdb.get('molecule', 'example.norbornene')

    #mol = datafile('tests/data/3ZJE.pdb').read('system')
    #mol = datafile('tests/data/naclwater.gro').read('system')
    mol.guess_bonds()

    v = QtMolecularViewer(mol)
    v.widget.background_color = colors.black
    v.widget.camera.autozoom(mol.r_array)

    def on_action1():
        if len(v.representation.selection) == 2:
            i, j = v.representation.selection
            distsq = ((mol.r_array[j] - mol.r_array[i])**2).sum()
            print('distance between', i, j, np.sqrt(distsq))

    def select_all_atoms():
        which = v.representation.selection[0]
        at = mol.type_array[which]
        sel = mol.type_array == at
        v.representation.make_selection(sel.nonzero()[0])

    def select_all_molecules():
        which = v.representation.last_modified
        if which is None:
            return

        at = mol.type_array[which]
        sel = mol.type_array == at
        allmol = mol.atom_to_molecule_indices(sel)
        allmol = mol.mol_to_atom_indices(allmol)
        v.representation.make_selection(allmol, additive=True)

    def change_representation():
        BallAndStickRepresentation = 0
        # We need two representations
        rep = v.add_representation(BallAndStickRepresentation, mol)
        rep.set_mask(self.selection)
        rep.set_mask(not self.selection)

    def scale_radii():
        #v.representation.scale_radii(v.representation.selection, 0.9)
        v.representation.hide(v.representation.selection)

    v.run()
