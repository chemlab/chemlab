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
>>> v.add_renderer(SphereRenderer, mol.atoms)
>>> v.run()

In this way you should be able to visualize a molecule in the VdW representation. In a similar fashion 
it is possible to display other features, such as boxes, arrows, highlight a subset of atoms etc.
