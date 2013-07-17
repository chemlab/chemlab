===========================
Installation and Quickstart
===========================

chemlab is currently tested on Ubuntu 13.04 and python 2.7, it should
work on 3.3 too. First install the dependencies::

    $ sudo apt-get install python-numpy python-scipy python-matplotlib python-pyside python-opengl cython 

`Download
<https://pypi.python.org/packages/source/c/chemlab/chemlab-0.3.tar.gz>`_
unpack and install chemlab from the setup.py included in the package::

    $ wget https://pypi.python.org/packages/source/c/chemlab/chemlab-0.3.tar.gz
    $ tar xvzf chemlab-0.3.tar.gz
    $ cd chemlab-0.3
    $ sudo python setup.py build_ext --inplace
    $ sudo python setup.py install

Test the newly installed package by typing::

    $ chemlab view tests/data/cry.gro

The molecular viewer should display a crystal, if not, file an issue
on `github <http://github.com/chemlab/chemlab/issues>`_.

.. image:: _static/licl.png
           :width: 600px

Once you're setup, you're ready to to dig in chemlab's
features. You may start from the :ref:`user-manual`.

Developement
------------

After installing the dependencies, grab the chemlab source from git::

    $ git clone --recursive https://github.com/chemlab/chemlab.git
   
Complile the included extensions::

    $ python setup.py build_ext --inplace

Just add the chemlab directory to the PYTHONPATH in your .bashrc::

    export PYTHONPATH=$PYTHONPATH:/path/to/chemlab
