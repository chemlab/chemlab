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

Molecules are easily and efficiently manipulated through the use of numpy arrays. One of the
most useful arrays contained in Molecule is the array of coordinates Molecule.r_array.
The array of coordinates is a numpy array of shape $(3xN)$ where $N$ is the number of atoms in the 
molecule.
 According to the numpy broadcasting rules, if you the sum with an array with 3 components (3xN) + (3,), 
each row of the matrix get summed by this quantity. Let's say we have a water molecule and we want to displace it randomly in a box, this is 
easily accomplished by initializing a Molecule around the origin and translating it.::

    import numpy
    wat = Molecule(...)
    wat.r_array += np.random.rand(3)

Using the same principles you can also apply other kind of transformation such as matrices. 
You can for example rotate the molecule about 90 degrees around the z-axis::

    from chemlab.transformations import rotation_matrix
    
    M = rotation_matrix(np.array([0.0, 0.0, 1.0]), np.pi/2)

    # slow, readable way
    for i,r in enumerate(wat.r_array):
        wat.r_array[i] = np.dot(M,r)

    # numpy efficient trick to do the same:
    # wat.r_array = M * wat.r_array.transpose()


Systems
-------

In molecular simulations it is customary to introduce a new data structure 
called System. This represents a collection of Molecules that will evolve 
during the simulation::

   s = System(molecules) # molecule is a list of Molecule instances

System do not take directly Atom as its constituents, therefore if you need to simulate
a system made of single atoms (say, a box of liquid Ar) you need to wrap the atoms in a 
Molecule::

   >>> ar = Atom('Ar', [0.0, 0.0, 0.0])
   >>> mol = Molecule([ar])

Also System exposes arrays to be used, and more molecules can be added to a System besides initialization. System,
similarly to Molecule can expose data.



Selecting groups in a System
----------------------------

Say you want to select the molecules around a certain point in space, you can use the function select_molecules that
will return you a set of indices corresponding to those molecules. on a similar fashion there is select_atoms.

    s.select_molecules(lambda mol: mol.geometric_centre < np.array([1.0, 1.0, 1.0]))
    [0, 2, 3, 6, 8 ...]

