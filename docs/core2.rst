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

    tpl = Molecule(...)
    space = 1.0
    for i in range(3):
        m.r_array += space
        sys.add(m)
    

     


