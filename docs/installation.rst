===========================
Installation and Quickstart
===========================

chemlab is currently tested on Ubuntu 12.10. First
install the dependencies::

    $ sudo apt-get install python-numpy python-scipy python-pyside python-opengl cython

Download chemlab and install it from the setup.py included in the
package::

    $ sudo python setup.py install

Test the newly installed package by typing::

    $ chemlab view tests/data/licl.gro

The molecular viewer should display a crystal, if not, file an issue
on `github <http://github.com/chemlab/chemlab/issues>`_.

.. image:: _static/licl.png
           :width: 600px

Once you're setup you're ready to go to dig in chemlab's features.

Quickstart
----------

We'll see how to read, visualize and process a proteine using chemlab.

    
Development
-----------

Grab the chemlab source from git::

    $ git clone https://github.com/chemlab/chemlab.git
   
Just add the chemlab directory to the PYTHONPATH in your .bashrc::

    export PYTHONPATH=$PYTHONPATH:/path/to/chemlab







