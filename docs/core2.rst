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

Now, imagine that we want a system comprised of multiple water molecules disposed on a line::

    m = Molecule(...)
    space = 1.0
    for i in range(3):
        m.r_array += space
        s.add(m)

This shows a very important thing about chemlab, Molecules act as containers of data and when you add them
to a system the data gets copied, in other words, System has no reference to the Molecule that you added.
While this may seem conterintuitive, this was made to avoid bad side-effects and confusion. Anyway, chemlab 
provides a simple way to track changes of a particular molecule and this is done in this way::

    m = Molecule(...)
    space = 1.0
    ref = s.add(m)
    
the System.add method returns an internal reference of the molecule just added. In this way we can access 
and change properties of the molecule, and every change will reflect the current state of the system.


