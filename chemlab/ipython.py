"""Ipython integration

"""
from __future__ import absolute_import
from io import BytesIO
from chemlab.graphics.renderers import AtomRenderer, BoxRenderer, BallAndStickRenderer
from chemlab.graphics.qtviewer import QtViewer
from chemlab.core import Molecule, System
from OpenGL.GL import *

from IPython.display import Image as ipy_Image
from PIL import Image as pil_Image


def load_ipython_extension(ipython):
    # The `ipython` argument is the currently active `InteractiveShell`
    # instance, which can be used in any way. This allows you to register
    # new magics, plugins or aliases, for example.
    png_formatter = ipython.display_formatter.formatters['image/png']
    png_formatter.for_type(Molecule, mol_to_png)
    png_formatter.for_type(System, sys_to_png)

def unload_ipython_extension(ipython):
    # If you want your extension to be unloadable, put that logic here.
    return

def showmol(mol, style='ball-and-stick',
            width=300, height=300):
    v = QtViewer()
    w = v.widget
    w.initializeGL()    
    
    if style == 'ball-and-stick':
        bs = v.add_renderer(BallAndStickRenderer,
                            mol.r_array,
                            mol.type_array,
                            mol.bonds)
    elif style == 'vdw':
        sr = v.add_renderer(AtomRenderer, mol.r_array, mol.type_array,
                            backend='impostors')

    w.camera.autozoom(mol.r_array)
    
    image = w.toimage(width, height)
    b = BytesIO()
    image.save(b, format='png')
    data = b.getvalue()
    
    # Cleanup
    del v
    del w
    
    # Save as png
    return ipy_Image(data=data)

def mol_to_png(mol):
    return showmol(mol)._repr_png_()

def showsys(sys, width=400, height=400):
    v = QtViewer()
    w = v.widget
    w.initializeGL()
    
    sr = v.add_renderer(AtomRenderer, sys.r_array, sys.type_array,
                        backend='impostors')
    
    if sys.box_vectors is not None:
        v.add_renderer(BoxRenderer, sys.box_vectors)
    
    w.camera.autozoom(sys.r_array)
    
    w.camera.orbit_y(-3.14/4)    
    w.camera.orbit_x(-3.14/4)

    image = w.toimage(width, height)
    b = BytesIO()
    image.save(b, format='png')
    data = b.getvalue()
    
    # Cleanup
    del v
    del w
    # Save as png
    return ipy_Image(data=data)

def sys_to_png(syst):
    return showsys(syst)._repr_png_()
