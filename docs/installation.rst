===========================
Installation and Quickstart
===========================


The easiest way to install chemlab is to use the Anaconda python distribution from the following link.

http://continuum.io/downloads

Then you can run the following command:

    conda install -c http://conda.binstar.org/gabrielelanaro chemlab

You can also install chemlab on Ubuntu 14.04 using apt. First install the dependencies:

    $ sudo apt-get install python-numpy python-scipy python-opengl cython python-matplotlib python-qt4-gl python-qt4

Then install chemlab from the setup.py included:

    $ sudo python setup.py install

NOTE: For python3 support install the corresponding python3
      packages available in your distribution or use pip.

Once you're setup, you're ready to to dig in chemlab's
features. You may start from the :ref:`user-manual`.

Development
------------

After installing the dependencies, grab the chemlab source from git::

    $ git clone --recursive https://github.com/chemlab/chemlab.git
   
Complile the included extensions::

    $ python setup.py build_ext --inplace

Just add the chemlab directory to the PYTHONPATH in your .bashrc::

    export PYTHONPATH=$PYTHONPATH:/path/to/chemlab
