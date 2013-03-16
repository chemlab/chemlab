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

Renderers are simply classes used to draw 3D objects. They are
tecnically required to provide just one method, *draw*. In this way
they provide the maximum flexibility required to build efficient
opengl routines. Renderers may be subclass other renderers as well
as use other renderers.

A very useful renderer is TriangleRenderer, used to render efficiently
a list of triangles, it constitutes a base for writing other
renderers. TriangleRenderer works basically like this, you pass the
vertices, normals and colors of the triangle and it will display a
triangle in the world::

    from chemlab.graphics import QtViewer
    from chemlab.graphics.renderers import TriangleRenderer
    from chemlab.graphics.colors import green
    import numpy as np
     
    vertices = np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]])
    normals = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0]])
    colors = np.array([green, green, green])
     
    v = QtViewer()
    v.add_renderer(TriangleRenderer, vertices, normals, colors)
    v.run()

.. image:: _static/graphics_triangle.png
	   :width: 600px
		   
If you pass 6 vertices/normals/colors, he will display 2 triangles and
so on. As a sidenote, he is very efficient and in fact
TriangleRenderer is used as a backend for a lot of other renderers
such as SphereRenderer and CylinderRenderer. If you can reduce a shape
in triangles, you can easily write a renderer for it.

In addition to that, TriangleRenderer provides also a method to update
vertices, normals and colors. We can demonstrate that from the last
example by defining an update function that rotates our triangle::
  
  from chemlab.graphics.transformations import rotation_matrix

  def update():
      y_axis = np.array([0.0, 1.0, 0.0])
      
      # We take the [:3,:3] part because rotation_matrix can be used to 
      # rotate homogeneous (4D) coordinates. 
      rot = rotation_matrix(3.14/32, y_axis)[:3, :3]
   
      # This is the numpy equivalent to applying rot to each coordinate
      vertices[:] = np.dot(vertices, rot.T)
      normals[:] = np.dot(vertices, rot.T)
      
      tr.update_vertices(vertices)
      tr.update_normals(normals)
      v.widget.repaint()
   
  v.schedule(update, 10)
  v.run()

On this ground we can develop a TetrahedronRenderer based on our
TriangleRenderer. To do that we first need to understand how a
tetrahedron is made, and how can we define the vertices that make the
tetrahedron.


