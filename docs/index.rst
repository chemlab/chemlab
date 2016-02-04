.. chemlab documentation master file, created by
   sphinx-quickstart on Sun Nov 18 21:31:35 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
   
Welcome to chemlab's documentation!
===================================

:Author:
   Gabriele Lanaro
   
:Contributors:
   Yotam Y. Avital, Adam Jackson

:Webpage:
   https://chemlab.github.com/chemlab
 
:Project Page:
   https://github.com/chemlab/chemlab

:Mailing List:
   `python-chemlab.googlegroups.com <mailto:python-chemlab.googlegroups.com>`_
   
:Downloads:
   https://chemlab.github.com/chemlab

Chemlab is a library that can help the user with chemistry-relevant
calculations using the flexibility and power of the python programming
language. It aims to be well-designed and pythonic, taking inspiration
from projects such as numpy and scipy.

Chemlab's long term goal is to be:

- **General**
  Chemistry is a huge field, chemlab wants to provide a general ground from where to build domain-specific tools and apps.
- **Array oriented** 
  Most operations and data structures are based on
  numpy arrays.  This let you write compact and efficient
  code.
- **Graphic**
  chemlab integrates a 3D molecular viewer that is easily
  extendable and lets you write your own visualization tools.
- **Interoperable**
  chemlab wants to be interoperable with other
  chemistry programs by reading and writing different
  file formats and using flexible data structures.
- **Fast**
  Even if python is known to be slow every effort should be made
  to make chemlab 'fast enough', by using effectively numpy arrays
  and efficient data structures. When everything else fails we can still
  write the hard bits in C with the help of cython.

Current Status
--------------

Computational and theoretical chemistry is a huge field, and providing
a program that encompasses all aspects of it is an impossible task. The
spirit of chemlab is to provide a common ground from where you can
build specific programs. For this reason it includes a :doc:`fully
programmable </graphics>` molecular viewer.

Chemlab includes a lot of utilities to programmatically download and
generate geometries. The molecular viewer is very fast (it can easily
*animate* ~100000 spheres) and the design is simple and flexible. For
more information about the newest features check out the release notes
in the :doc:`whatsnew` document.

Chemlab is developer-friendly, it provides good documentation and has
an easy structure to get in. Feel free to send me anything that you
may do with chemlab, like supporting a new file format, a new graphic
renderer, a nice example, even if you don't think it's perfect. File an issue 
on the github page to discuss any idea that comes to your mind. Get involved!

.. _user-manual:

User Manual
-----------

.. toctree::
   
   whatsnew

**Table of Contents**

.. toctree::
   :maxdepth: 2
  
   installation
   core
   io
   graphics
   db
   mviewer
   ipython
   gromacs

Reference Documentation
-----------------------

**Packages**

.. toctree::
   :maxdepth: 2

   api/chemlab.core
   api/chemlab.io
   api/chemlab.graphics
   api/chemlab.db
   api/chemlab.utils
   api/chemlab.mviewer.api
   api/chemlab.qc
   api/chemlab.notebook

License
-------

Chemlab is released under the `GNU GPLv3
<http://www.gnu.org/licenses/gpl.html>`_ and its main developer is
Gabriele Lanaro.
