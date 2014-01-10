from core import *
from select_ import *
from orderpar import *
from chemlab.graphics import colors
import numpy as np

def change_background(color):
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
    
def _color_from_str(color):
    try:
        col = getattr(colors, color)
    except:
        print('No color like this')
    return col
    
def change_color(color):
    atms = selected_atoms()
    rep = current_representation()
    
    # Let's parse the color first
    if isinstance(color, str):
        # The color should be a string
        col = _color_from_str(color)
        rep.atom_colors[atms,0:3] = col[0:3]
    if isinstance(color, list):
        if isinstance(color[0], str):
            cols = [_color_from_str(c) for c in color]
            cols = np.array(cols)
        
        rep.atom_colors[atms, 0:3] = cols[:, 0:3]
        
    if isinstance(color, np.ndarray):
        cols = color
        print len(cols), len(atms)
        rep.atom_colors[atms, 0:3] = cols[:, 0:3]

def reset_color():
    atms = selected_atoms()
    rep = current_representation()
    
    if len(atms) == 0:
        rep.atom_colors.reset()

    rep.atom_colors[atms,0:3] = np.array(rep.atom_colors.default)[atms,0:3]


def change_default_radii(def_map):
    s = current_system()
    rep = current_representation()
    rep.radii_state.default = [def_map[t] for t in s.type_array]
    rep.radii_state.reset()
    scale_atoms()
    
def change_hue(amount):
    rep = current_representation()
    rgb_cols = np.array(rep.atom_colors.array)[:, 0:3]
    hsl_cols = colors.rgb_to_hsl(rgb_cols)
    hsl_cols[:, 0] = np.clip(hsl_cols[:, 0] + amount, 0, 254)
    
    print rgb_cols[0]
    print hsl_cols[0]
    rgb_cols = colors.hsl_to_rgb(hsl_cols)
    print rgb_cols[0]
    rep.atom_colors[:, 0:3] = rgb_cols
    
    
def change_saturation(amount):
    rep = current_representation()
    rgb_cols = np.array(rep.atom_colors.array)[:, 0:3]
    hsl_cols = colors.rgb_to_hsl(rgb_cols)
    hsl_cols[:, 1] = np.clip(hsl_cols[:, 1] + amount, 0, 254)
    
    print rgb_cols[0]
    print hsl_cols[0]

    rgb_cols = colors.hsl_to_rgb(hsl_cols)
    print rgb_cols[0]
    
    rep.atom_colors[:, 0:3] = rgb_cols
    
def change_lightness(amount):
    rep = current_representation()
    rgb_cols = np.array(rep.atom_colors.array)[:, 0:3]
    hsl_cols = colors.rgb_to_hsl(rgb_cols)
    hsl_cols[:, 2] = np.clip(hsl_cols[:, 2] + amount, 0, 255)
    
    rgb_cols = colors.hsl_to_rgb(hsl_cols)
    rep.atom_colors[:, 0:3] = rgb_cols

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
