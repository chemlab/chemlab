from core import *
from selections import *
from chemlab.graphics import colors
import numpy as np

def color_from_string(color):
    """Given a string *color*, return the color as a tuple (r, g, b,
    a) where each value is between 0 and 255.

    As for the color name follow the `HTML color names
    <http://www.w3schools.com/tags/ref_colornames.asp>` in lowescore
    style eg. *forest_green*.

    """

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
    

    .. seealso:: :py:func:`chemlab.mviewer.api.color_from_string`

    """
    viewer.widget.background_color = color_from_string(color)
    viewer.update()

# That's kinda of a MAYBE API
def change_appeareance(keyval):
    raise NotImplementedError()

def get_appeareance(keyval):
    raise NotImplementedError()
    
def change_radius(value):
    '''Change the radius of the currently selected atoms by a certain
    *value*.

    If *value* is None, set the radius to the default value.

    '''
    current_representation().change_radius(current_representation().selection_state, value)

def scale_atoms(fac):
    '''Scale the currently selected atoms atoms by a certain factor
    *fac*.

    Use the value *fac=1.0* to reset the scale.

    '''
    rep = current_representation()
    atms = selected_atoms()
    rep.scale_factors[atms] = fac
    
    rep.update_scale_factors(rep.scale_factors)
    viewer.update()


def change_color(color):
    """Change the color of the currently selected objects. *color* is
    represented as a string. Otherwise color can be passed as an rgba tuple of values between 0, 255

    Reset the color by passing *color=None*.

    """
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
    """Change the default radii
    """
    s = current_system()
    rep = current_representation()
    rep.radii_state.default = [def_map[t] for t in s.type_array]
    rep.radii_state.reset()
    #scale_atoms(None)
    
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

_counter = 0

from collections import OrderedDict
_effect_map = OrderedDict()

def add_post_processing(effect,  **options):
    """Apply a post processing effect.

    **Parameters**
    
    effect: string
        The effect to be applied, choose between ``ssao``,
        ``outline``, ``fxaa``, ``gamma``.
    
    **options:
        Options used to initialize the effect, check the
        :doc:`chemlab.graphics.postprocessing` for a complete
        reference of all the options.
    
    **Returns**

    A string identifier that can be used to reference the applied effect.

    """

    from chemlab.graphics.postprocessing import SSAOEffect, OutlineEffect, FXAAEffect, GammaCorrectionEffect
    
    pp_map = {'ssao': SSAOEffect,
              'outline': OutlineEffect,
              'fxaa': FXAAEffect,
              'gamma': GammaCorrectionEffect}
    
    pp = viewer.add_post_processing(pp_map[effect], **options)    
    viewer.update()


    global _counter
    _counter += 1
    
    str_id = effect + str(_counter)    
    _effect_map[str_id] = pp # saving it for removal for later...
    
    return str_id # That's an unique ID

def list_post_processing():
    """List all the post processing effects by name."""
    
    return list(_effect_map.keys())

def remove_post_processing(str_id):
    """Remove a post processing effect by passing its string id
    provided by
    :py:func:`~chemlab.mviewer.api.add_post_processing`.

    """
    
    viewer.remove_post_processing(_effect_map[str_id])
    
    # We need to remove the same from our dictionary
    del _effect_map[str_id]

def clear_post_processing():
    """Remove all post processing effects."""
    
    for str_id in list_post_processing():
        remove_post_processing(str_id)

def change_post_processing_options(str_id, **options):
    """Change the options of the post processing effect referred by
    its string id.

    """
    _effect_map[str_id].set_options(**options)
    viewer.update()