
from core import *
from select_ import *
from orderpar import *
from chemlab.graphics import colors

def background_color(color):
    """Setup the background color to *color* as a string
    """

    # The color should be a string
    try:
        col = getattr(colors, color)
    except:
        raise Exception('No color like this')
        
    viewer.widget.background_color = col
    viewer.update()


def scale_atoms(fac=None):
    rep = current_representation()
    atms = selected_atoms()
    if fac is None:
        rep.scale_factors[atms] = 1.0
    else:
        rep.scale_factors[atms] *= fac
    
    rep.update_scale_factors(rep.scale_factors)
    viewer.update()
    

def change_color(color):
    # The color should be a string
    try:
        col = getattr(colors, color)
    except:
        print('No color like this')
    
    atms = selected_atoms()
    rep = current_representation()
    rep.atom_colors[atms,0:3] = col[0:3]

def reset_color():
    atms = selected_atoms()
    rep = current_representation()
    
    if len(atms) == 0:
        rep.atom_colors[:,0:3] = rep.default_colors[:,0:3]

    rep.atom_colors[atms,0:3] = rep.default_colors[atms,0:3]

def screenshot(filename, width=600, height=600):
    img = viewer.widget.toimage(width, height)
    img.save(filename)

def change_shading(shader):
    rep = current_representation()
    rep.atom_renderer.change_shading(shader)

from chemlab.graphics.postprocessing import *

def add_post_processing(pp, **kwargs):
    viewer.add_post_processing(pp, **kwargs)
    viewer.update()

def list_post_processing():
    pass

def remove_post_processing(pp):
    pass
    
def post_processing_options(pp, options):
    pass
