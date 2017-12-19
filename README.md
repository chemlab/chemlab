chemlab - the python chemistry package you were waiting for
===========================================================


[![Join the chat at https://gitter.im/chemlab/chemlab](https://badges.gitter.im/chemlab/chemlab.svg)](https://gitter.im/chemlab/chemlab?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

[![Downloads](https://img.shields.io/pypi/dm/chemlab.svg)](https://crate.io/package/chemlab)
[![Build Status](https://travis-ci.org/chemlab/chemlab.svg?branch=master)](https://travis-ci.org/chemlab/chemlab)

- Version: 1.0b1
- Author: Gabriele Lanaro
- Contributors: Yotam Y. Avital, Adam Jackson, Jaime Rodriguez-Guerra
- Email: python-chemlab@googlegroups.com
- Website: http://chemlab.github.com/chemlab
- Docs: http://chemlab.rtfd.org
- Github: http://github.com/chemlab/chemlab

Project status
--------------

chemlab is not being maintained anymore, if you would like to adopt chemlab, send an email @gabrielelanaro!

Description
-----------
chemlab is a python library and a set of utilities built to ease the
life of the computational chemist. It takes inspiration from other
python scientific library such as numpy, scipy and matplotlib, and aims
to bring a consistent and simple API by following the python
guidelines.



Computational and theoretical chemistry is a huge field, and providing
a program that encompasses all aspect of it is an impossible task. The
spirit of chemlab is to provide a common ground from where you can
build specific programs. For this reason it includes an easily
extendable molecular viewer and flexible field-independent data
structures.

chemlab is looking for contributors, it includes a good documentation
and has an easy structure to get in. Feel free to send me anything that
you may do with chemlab, from supporting a new file format to writing
a new graphic renderer, even if you don'think it's perfect. Send me an
email or write an issue on the github page.

Installation
------------

TIP: more updated instructions are located in the docs:
     http://chemlab.readthedocs.org/en/latest/installation.html

The easiest way to install chemlab is to use the Anaconda python distribution from the following link.

http://continuum.io/downloads

Then you can run the following command:

    conda install -c http://conda.binstar.org/gabrielelanaro chemlab

Documentation
-------------

Refer to the documentation link at the beginning of this file.

Bug Reports
-----------

Go to http://github.com/chemlab/chemlab or send an email to python-chemlab@googlegroups.com.

License
-------

chemlab is released under the GNU GPL3 or GNU LGPL license if the PyQt parts are omitted (such as chemlab.graphics and chemlab.mviewer packages) and the chemlab.core.crystal package is omitted as well. See lgpl.txt and gpl.txt files attached.
