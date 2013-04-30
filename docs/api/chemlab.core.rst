chemlab.core
============

This package contains general functions and the most basic data
containers such as Atom, Molecule and System. Plus some utility
functions to create and edit common Systems.
   
The Atom class
--------------

.. autoclass:: chemlab.core.Atom
    :members:

The Molecule class
------------------

.. autoclass:: chemlab.core.Molecule
    :members:

The System class
----------------

.. autoclass:: chemlab.core.System
    :members:
 
Routines to manipulate Systems
------------------------------

.. autofunction:: chemlab.core.subsystem_from_molecules
		  

.. autofunction:: chemlab.core.subsystem_from_atoms


.. autofunction:: chemlab.core.merge_systems


Routines to create Systems
--------------------------

.. autofunction:: chemlab.core.crystal

.. autofunction:: chemlab.core.random_lattice_box
