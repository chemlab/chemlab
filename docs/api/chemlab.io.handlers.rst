Supported File Formats
======================

cml: Chemical Markup Language
-----------------------------

:Extension: .cml

.. autoclass:: chemlab.io.handlers.CmlIO
	       :members:

edr: GROMACS energy file
------------------------

:Extension: .edr
	    
.. autoclass:: chemlab.io.handlers.EdrIO
	:members:


gro: GROMACS coordinate files
-----------------------------

:Extension: .gro

.. autoclass:: chemlab.io.handlers.GromacsIO
	:members:

mol: MDL Coordinate files
-------------------------

:Extension: .mol

.. autoclass:: chemlab.io.handlers.MolIO
	       :members:
	       
pdb: Protein Data Bank format
-----------------------------

:Extension: .pdb
	    
.. autoclass:: chemlab.io.handlers.PdbIO
		:members:
	    
xtc: GROMACS compressed trajectory file
---------------------------------------

:Extension: .xtc
	    
.. autoclass:: chemlab.io.handlers.XtcIO
		:members:
	    
xyz: XYZ coordinate format
--------------------------

:Extension: .xyz

.. autoclass:: chemlab.io.handlers.XyzIO
		:members:



``cclib`` integration
=====================

Those handlers are based on the cclib_ library. The `feature` names extracted match those of 
the one included in the cclib_ documentation.

Chemlab also extract a :class:`chemlab.core.Molecule` instance from the file through the
`feature` named ``molecule``.

List of file formats:

- gamess
- gamessuk
- gaussian
- jaguar
- molpro
- orca

You can also use the method ``available_properties`` to get the available properties dynamically.

.. _cclib: http://cclib.github.io 