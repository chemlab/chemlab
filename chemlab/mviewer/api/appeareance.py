from core import *
from selections import *
from chemlab.graphics import colors
import numpy as np

def color_from_string(color):
    # The color should be a string
    try:
        col = getattr(colors, color)
    except:
        raise ValueError('Color not found: {}'.format(color))
    return col

def change_background(color):
    """Setup the background color to *color*.
    
    Example::

      change_background('black')
      change_background('white')
    
    As for the color name follow those in lowescore style
    eg. 'forest_green'.

    """
    viewer.widget.background_color = color_from_string(color)
    viewer.update()

# That's kinda of a MAYBE API
def change_appeareance(keyval):
    raise NotImplementedError()

def get_appeareance(keyval):
    raise NotImplementedError()
    
def change_radius(value):
    '''Change the radius of each atom by a certain *value*.

    If *value* is None, set the radius to the default value.
    '''
    current_representation().change_radius(current_representation().selection_state, value)

def scale_atoms(fac):
    '''Scale the atoms by a certain factor *fac*.

    Use the value *fac=1.0* to reset the scale.

    '''
    rep = current_representation()
    atms = selected_atoms()
    rep.scale_factors[atms] *= fac
    
    rep.update_scale_factors(rep.scale_factors)
    viewer.update()


def change_color(color):
    """Change the color of the currently selected objects. *color* is
    represented as a string.

    Reset the color by passing *color=None*.

    """

    atms = selected_atoms()
    rep = current_representation()
    
    # Let's parse the color first
    if isinstance(color, str):
        # The color should be a string
        col = color_from_string(color)

    if isinstance(color, tuple):
        col = color
        
    if color is None:
        col = None

    # Color array
    rep.change_color(rep.selection_state, col)

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
    '''Make a screenshot of the current view. You can tweak the
    resolution up to what your GPU memory supports.
    
    Example::

      screenshot('screen.png', 1200, 1200)
    
    '''
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
