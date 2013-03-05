.. chemlab documentation master file, created by
   sphinx-quickstart on Sun Nov 18 21:31:35 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to chemlab's documentation!
===================================

chemlab is designed to be a library that can be used to perform
chemistry-relevant calculations with the flexibility and power of the
python programming language. It aims to be well-designed and pythonic,
taking inspiration from project such as numpy and scipy.

Features (Planned):

* array oriented: most operations and data structures are based on numpy arrays.
               This let you write compact and efficient code.
* visualization: chemlab includes a 3D molecular viewer. It is designed to be easily extendable
               and to write your own tools in a programmatic way.
* convenience: chemlab aim is to be interoperable with other chemistry programs, making it useful to 'glue toghether'
               different functions.

The current status of chemlab
-----------------------------

chemlab is still in its infancy and it provides the most basic data structures. It's important to get them right now 
to avoid problems in the future. The molecular viewer (chemlab.graphics) has a solid ground and can actually draw 
and play trajectories in an efficient way. More representations are required to enrich its capabilities.


Contents:

.. toctree::
   :maxdepth: 2
   
   intro
   graphics


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

