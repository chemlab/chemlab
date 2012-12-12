Graphics
========

The ``chemlab.graphics`` package is one of the most interesting aspects of chemlab, that sets him apart from similar 
programs.

The purpose of the package is to provide a solid library to develop 3D applications to display chemical data
in an flexible way. For example it's extremely easy to build a molecular viewer and add a bunch of custom features
to it.

The typical approach when developing a graphics application is to create a ``Viewer`` instance and add 
3D features to it::

>>> from chemlab.graphics import Viewer
>>> v = Viewer()

now, assuming that we have an already defined molecule, let's proceed to add some features to it::

>>> from chemlab.graphics.renderers import SphereRenderer
>>> sphere_renderer = v.add_renderer(SphereRenderer, mol.atoms)
>>> v.run()

In this way you should be able to visualize a molecule in the VdW representation. In a similar fashion 
it is possible to display other features, such as boxes, arrows, highlight a subset of atoms etc.
It can be noticed that with add_renderer we are not passing an *instance* of the renderer, but we're passing
the renderer *class* and its respective constructor arguments. The method ``Viewer.add_renderer`` returns the 
actual instance

The user interaction is introduced in a similar fashion. The module ``chemlab.graphics`` provides different 
``Widget`` classes to provide the most common user interaction using the pyglet framework. For example adding a 
slider widget can be done in this way::

    from chemlab.graphics.ui import SliderUI
    slider = v.add_ui(SliderUI, x=100, y=50, width=300, height=100, range_=10)
    
    @slider.event
    def on_update(pos):
       # Do something when the slider cursor is moved on *pos*
       # that is an integer between 0 and *range_* - 1
       return

This will display a slider with 10 spaced ticks and when it is moved it will trigger the *on_update*
callback.


