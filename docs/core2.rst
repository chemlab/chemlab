chemlab provides some data structures to handle the physical objects useful
in molecular simulation. They are optimized for efficiency and compatibility with
C interfaces through the use of the numpy library and they're also designed to 
cover the common manipulation use cases..

To illustrate how they are built and what their interaction are let's look at some examples.
In a typical molecular simulation you may want to define a system composed of different bodies, that
we may identify with molecules. For example let's consider a system comprised of a single water molecule. in the 
chemlab language we have to define a molecules and add this molecule to the System.

    >>> m = Molecule(Atom("H", [0.0, 0.0, 0.0]), Atom("H", [0.0, 1.0, 0.0]), Atom("O", [0.0, 0.0, 1.0]))
    >>> s = System()
    >>> s.add(m)

Now, imagine that we want a system comprised of 10 spaced water molecules disposed on the x-axis. A good 
strategy to build such a system would be to add multiple water molecules by 
traslating along the x-axis the coordinates of each atom, the Molecule class let you access directly the 
atoms coordinate array through the attribute r_array, in the following snippet we used the 
broadcasting to add the array [1.0, 0.0, 0.0] to each of the position of each atom::

    m = Molecule(...)
    dr = np.array([0.0, 0.0, 0.0])
    for i in range(3):
        m.r_array += dr
        s.add(m)

There's a very important thing about chemlab, Molecules act as containers of data and when you add them
to a system the data gets copied, in other words, System has no reference to the Molecule that you added.
While this may seem conterintuitive, this helps with uncontrolled propagation of side effects, increases memory 
efficiency and helps with the use of numpy arrays for computation. Anyway, chemlab provides a simple way to track 
changes of a particular molecule. the System.add method returns an internal reference of the
molecule just added. In this way we can access  and change properties of the molecule, 
and every change will reflect the current state of the system.

    m = Molecule(...)
    space = 1.0
    ref = s.add(m)
    



