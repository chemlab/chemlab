Atoms and Molecules
-------------------

In chemlab, atoms can be represented using the Atom data structure,
and it contains some common information about our particles like type, mass
and position. Atom instances are easily created by initializing them with data obtained in appropriate
[[units]]::

    >>> ar = Atom('Ar', [0.0, 0.0, 0.0])
    >>> ar.type
    'Ar'
    >>> ar.r
    np.array([0.0, 0.0, 0.0])

A Molecule is an entity composed of more atoms and most of the Molecule properties
are inherited from the constituent atoms. To initialize a Molecule you can, for example
pass a list of atom instances to its constructor::

    >>> mol = Molecule([at1, at2, at3])

There are two main ways to access atomic data in Molecules, by arrays or by atom.
This is done to provide a massive increase in performance and a more straightforward
integration with C libraries through a generous use of numpy arrays. This decision comes 
at a cost: the data contained in the atom that you pass to the constructor is copied 
into the molecule, this means that change in the costituents atoms are not reflected to
the Molecule and viceversa. At first sight this may seem a big problem, but actually it
isn't as we will see in the following examples.

Manipulating Molecules
----------------------

Molecules are easily and efficiently manipulated through the use of arrays. Let's
say we have a water molecule. And we want to displace it randomly



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
