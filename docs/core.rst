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
 
System, similarly to Molecule can expose data by using arrays. By
default, system inherits the atomic data from the constituent
molecules, in this way you can easily and efficiently access all the
atomic coordinates by using the attribute
:py:attr:`System.r_array`. To understand the relation between Atom.r,
Molecule.r_array and System.r_array refer to the picture below.
 
.. image:: _static/core_types_copy.png
      :scale: 70 %
      :align: center

You can preallocate a `System` by using the classmethod
:py:meth:`System.empty <chemlab.core.System.empty>` (pretty much like
you can preallocate numpy arrays with `np.empty` or `np.zeros`) and
then add the molecules one by one::
  

  import numpy as np
  from chemlab.core import Atom, Molecule, System
  from chemlab.graphics import display_system
  
  # Template molecule
  wat = Molecule([Atom('O', [0.00, 0.00, 0.01]),
                  Atom('H', [0.00, 0.08,-0.05]),
                  Atom('H', [0.00,-0.08,-0.05])])
		  
  # Initialize a system with four water molecules.    
  s = System.empty(4, 12) # 4 molecules, 12 atoms
  
  for i in range(4):
      wat.move_to(np.random.rand(3)) # randomly displace the water molecule
      s.add(wat) # data gets copied each time
  
  display_system(s)

Since the data is copied, the ``wat`` molecule act as a `template` so
you can move it around and keep adding it to the System.

Preallocating and adding molecules is a pretty fast way to build a
`System`, but the fastest way (in terms of processing time) is to
build the system by passing ready-made arrays, this is done by using
:py:meth:`chemlab.core.System.from_arrays`.

Building Crystals
.................

chemlab provides an handy way to build crystal structures from the
atomic coordinates and the space group information. If you basically have
the crystallographic informations, you can easily build a crystal::

  from chemlab.core import Atom, Molecule, crystal
  from chemlab.graphics import display_system
  
  # Molecule templates
  na = Molecule([Atom('Na', [0.0, 0.0, 0.0])])
  cl = Molecule([Atom('Cl', [0.0, 0.0, 0.0])])
  
  s = crystal([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]], # Equivalent Positions
              [na, cl], # Molecules
	      225, # Space Group
	      cellpar = [.54, .54, .54, 90, 90, 90], # unit cell parameters
	      repetitions = [5, 5, 5]) # unit cell repetitions in each direction

  display_system(s)
	     
.. seealso:: :py:func:`chemlab.core.crystal`
	     
.. note:: If you'd like to implement a .cif file reader, you're
          welcome! Drop a patch on github.


Manipulating Systems
....................

You can manipulate systems by using some simple but flexible
functions. It is really easy to generate a system by selecting a part
from a bigger system, this is implemented in the functions
:py:func:`chemlab.core.subsystem_from_atoms` and
:py:func:`chemlab.core.subsystem_from_molecules`.

The following example shows an easy way to take the molecules that
are in the region of space `x > 0`::

  from chemlab.core import crystal



