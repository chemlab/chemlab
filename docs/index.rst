.. chemlab documentation master file, created by
   sphinx-quickstart on Sun Nov 18 21:31:35 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to chemlab's documentation!
===================================

chemlab is a library that can help the user with chemistry-relevant
calculations using the flexibility and power of the python programming
language. It aims to be well-designed and pythonic, taking inspiration
from project such as numpy and scipy.

chemlab long term goal is to be:

- array oriented: most operations and data structures are based on
               numpy arrays.  This let you write compact and efficient
               code.
- graphic: chemlab aim to integrate 3D molecular viewer that is easily
           extendable and lets you write your own visualization tools
           easily.
- interoperable: chemlab wants to be interoperable with other
               chemistry programs, to enable the integration of
               different functions from different programs.
- fast: Even if python is known to be slow every effort should be made
        to make chemlab 'fast enough', by using effectively numpy arrays
        and efficient data structures. When everything else fails we can still
        write the hard bits in C.


The current status of chemlab
-----------------------------

chemlab is still in its infancy and it provides the most basic data
structures. It's important to get them right to avoid problems in the
future. The molecular viewer (chemlab.graphics) has a solid ground and
can actually draw and play trajectories in an efficient way. More
representations are required to enrich its capabilities. It's still a
bit early to make useful as it is, but it can be a nice platform where
other programs can be built on.

chemlab is divided in several packages that can be used almost
independently.

  - chemlab.graphics includes a molecular viewer and its components.
  - chemlab.molsim molecular simulation routines
  - chemlab.core basic data structures such as atoms, molecules etc
  - chemlab.data database for various chemical data
  - chemlab.io input/output utilities and integration with other
    molecular packages.


User Manual:

.. toctree::
   :maxdepth: 2
  
   installation
   core
   io
   graphics
   gromacs
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

