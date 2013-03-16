==========================
Graphics and Visualization
==========================

Intro
-----

The ``chemlab.graphics`` package is one of the most interesting
aspects of chemlab, that sets him apart from similar programs.

The purpose of the package is to provide a solid library to develop 3D
applications to display chemical data in an flexible way. For example
it's extremely easy to build a molecular viewer and add a bunch of
custom features to it.

The typical approach when developing a graphics application is to
create a ``Viewer`` instance and add 3D features to it::

>>> from chemlab.graphics import QtViewer
>>> v = QtViewer()

now let's define a molecule. We can use the `moldb` module to get a
water template.

>>> from chemlab.graphics.renderers import SphereRenderer
>>> from chemlab.data.moldb import water
>>> ar = v.add_renderer(AtomRenderer, water)
>>> v.run()

.. image:: _static/graphics_water.png
    :width: 600px

In this way you should be able to visualize a molecule where each atom
is represented as a sphere. There are also a set of viewing controls:

- **Mouse Drag (Left Click) or Left/Right/Up/Down**:   Rotate the molecule

- **Mouse Drag (Right Click)**:  Pan the view
    
- **Mouse Wheel or +/-**:  Zoom in/out


In a similar fashion it is possible to display other features, such as
boxes, arrows, lines, etc.  It is useful to notice that with
``Viewer.add_renderer`` we are not passing an *instance* of the renderer, but
we're passing the renderer *class* and its respective constructor
arguments. The method ``Viewer.add_renderer`` returns the actual
instance.

It is possible as well to overlay 2D elements to a scene in a similar
fashion, this will display a string at the screen position 300, 300::

    from chemlab.graphics.uis import TextUI
    tui = v.add_ui(TextUI, 300, 300, "Hello, World!")
    
Anyway, I encourage you to use the powerful Qt framework to provide
interaction and widgets to your application.

Renderers
---------

Renderers are simply classes.
