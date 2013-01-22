In chemlab, atoms can be represented using the Atom data structure
and molecules using the Molecule data structure. Those two kind of
objects are easily created by initializing them with data::

    >>> ar = Atom('Ar', [0.0, 0.0, 0.0])
    >>> mol = Molecule([ar])

Some fields of those data structures are not mutable, for example you can't 
add further atoms to a Molecule, we do this to avoid syncronization issues 
when we're going to use the Molecule class in superior data structures. 
Most of the attributes are accessible throught simple attributes::

   >>> ar.type
   'Ar'
   >>> ar.coord
   np.array([0.0, 0.0, 0.0])

In molecular simulations it is customary to introduce a new data structure 
called System. This represents a collection of Molecules that will evolve 
during the simulation::

   s = System(molecules) # molecule is a list of Molecule instances

System do not take directly Atom as its constituents, therefore if you need to simulate
a system made of single atoms (say, a box of liquid Ar) you need to wrap the atoms in a 
Molecule::

   >>> ar = Atom('Ar', [0.0, 0.0, 0.0])
   >>> mol = Molecule([ar])

Anyway, there are multiple ways to get started with a System in chemlab, to provide a
fast way to build initial configurations for your simulation run.
