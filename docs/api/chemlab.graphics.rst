chemlab.graphics
================

This package contains the features related to the graphic capabilities
of chemlab.

Ready to use functions
----------------------

The two following functions are a convenient way to quickly display 
and animate a :py:class:`~chemlab.core.System` in chemlab.

.. autofunction:: chemlab.graphics.display_system
		 
.. autofunction:: chemlab.graphics.display_trajectory		 



Builtin 3D viewers
-------------------

The QtViewer class
..................

.. autoclass:: chemlab.graphics.QtViewer
    :members:

The QtTrajectoryViewer class
............................

.. autoclass:: chemlab.graphics.QtTrajectoryViewer
     :members:
	
Renderers and UIs
-----------------

.. toctree::
    chemlab.graphics.renderers

.. toctree::
    chemlab.graphics.uis
    
Post Processing Effects
-----------------------

.. toctree::
    chemlab.graphics.postprocessing

Low level widgets
-----------------

The QChemlabWidget class
........................

This is the molecular viewer widget used by chemlab.

.. autoclass:: chemlab.graphics.QChemlabWidget
    :members:

The Camera class
................

.. autoclass:: chemlab.graphics.camera.Camera
    :members:

Transformations
---------------

.. toctree:: chemlab.graphics.transformations
