============================
Atoms, Molecules and Systems
============================

In chemlab, atoms can be represented using the Atom data structure,
and it contains some common information about our particles like type,
mass and position. Atom instances are easily created by initializing
them with data obtained in appropriate units, for the atomic coordinates
you should use nanometers::

    >>> from chemlab.core import Atom
    >>> ar = Atom('Ar', [0.0, 0.0, 0.0])
    >>> ar.type
    'Ar'
    >>> ar.r
    np.array([0.0, 0.0, 0.0])

A Molecule is an entity composed of more atoms and most of the
Molecule properties are inherited from the constituent atoms. To
initialize a Molecule you can, for example pass a list of atom
instances to its constructor::

    >>> from chemlab.core import Molecule
    >>> mol = Molecule([at1, at2, at3])

There are two main ways to access atomic data in Molecules, by arrays
or by atom.  

Manipulating Molecules
----------------------

Molecules are easily and efficiently manipulated through the use of
numpy arrays. One of the most useful arrays contained in Molecule is
the array of coordinates Molecule.r_array.  The array of coordinates
is a numpy array of shape ``(NA,3)`` where ``NA`` is the number of
atoms in the molecule.  According to the numpy broadcasting rules, if
you the sum with an array with 3 components ``(NA,3)`` + ``(3,)``,
each row of the coordinate array get summed by this quantity. Let's
say we have a water molecule and we want to displace it randomly in a
box, this is easily accomplished by initializing a Molecule around the
origin and translating it::

    import numpy as np
    
    wat = Molecule([Atom("H", [0.0, 0.0, 0.0]),
                    Atom("H", [0.0, 1.0, 0.0]),
                    Atom("O", [0.0, 0.0, 1.0])])
    
    wat.r_array += np.random.rand(3)

Using the same principles you can also apply other kind of
transformation such as matrices.  You can for example rotate the
molecule about 90 degrees around the z-axis::

    from chemlab.graphics.transformations import rotation_matrix
    
    # The transformation module returns 4x4 matrices
    M = rotation_matrix(np.pi/2, np.array([0.0, 0.0, 1.0]))[:3,:3]

    # slow, readable way
    for i,r in enumerate(wat.r_array):
        wat.r_array[i] = np.dot(M,r)

    # numpy efficient trick to do the same:
    # wat.r_array = np.dot(wat.r_array, M.T)

The array-based interaction is done provide a massive increase in performance
and a more straightforward integration with C libraries through a
generous use of numpy arrays. This decision comes at a cost: the data
contained in the atom that you pass to the constructor is copied into
the molecule, this means that change in the costituents atoms are not
reflected to the Molecule and viceversa. At first sight this may seem
a big problem, but actually it isn't because it limits unexpected 
side effects making the code more predictable.

Systems
-------
 
In molecular simulations it is customary to introduce a new data
structure called System. This represents a collection of Molecules
that will evolve during the simulation::
 
   >>> from chemlab.core import System
   >>> s = System(molecules) # molecule is a list of Molecule instances
 
System do not take directly Atom as its constituents, therefore if you
need to simulate a system made of single atoms (say, a box of liquid
Ar) you need to wrap the atoms in a Molecule::
 
   >>> ar = Atom('Ar', [0.0, 0.0, 0.0])
   >>> mol = Molecule([ar])
 
Also System exposes arrays to be used, and more molecules can be added
to a System besides initialization. System, similarly to Molecule can
expose data by using arrays. By default, system inherits the atomic
data from the constituent molecules, in this way you can, for
instance, easily and efficienntly iterate over the atomic coordinates by
using the attribute System.r_array. To understand the relation between 
Atom.r, Molecule.r_array and System.r_array refer to the picture below.
 
.. image:: _static/core_types_copy.png
      :scale: 70 %
      :align: center


..
   Selecting groups in a System
   ----------------------------
    
   Say you want to select a subsystem of 
    
       s.select_molecules()
       [0, 2, 3, 6, 8 ...]
    
   To illustrate how they are built and what their interaction are let's
   look at some examples.  In a typical molecular simulation you may want
   to define a system composed of different bodies, that we may identify
   with molecules. For example let's consider a system comprised of a
   single water molecule. in the chemlab language we have to define a
   molecules and add this molecule to the System.
    
    
       >>> s = System()
       >>> s.add(m)
    
   Now, imagine that we want a system comprised of 10 spaced water
   molecules disposed on the x-axis. A good strategy to build such a
   system would be to add multiple water molecules by traslating along
   the x-axis the coordinates of each atom, the Molecule class let you
   access directly the atoms coordinate array through the attribute
   r_array, in the following snippet we used the broadcasting to add the
   array [1.0, 0.0, 0.0] to each of the position of each atom::
    
       m = Molecule(...)
       dr = np.array([0.0, 0.0, 0.0])
       for i in range(3):
           m.r_array += dr
           s.add(m)
    
   In a certain sense, a Molecule instance acts as a template to build your
   system.
