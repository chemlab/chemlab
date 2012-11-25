In chemblab, atoms can be represented using the Atom data structure
and molecules using the Molecule data structure. Those two kind of
objects are easily created from data::

    >>> ar = Atom('Ar', [0.0, 0.0, 0.0])

They are meant to be used as containers of data and they have
attributes used to access these properties.

   >>> ar.type
   'Ar'
   >>> ar.coord
   np.array([])

