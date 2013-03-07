===========================
Installation and Quickstart
===========================

In its early stages, chemlab does not provide yet a package for
automatic installation, but it will for sure. Anyway, it's based on
popular libraries already available on most Linux distributions, other
platforms are not taken into account yet, but the will be at a certain
point.

Core dependencies:

    sudo apt-get install python-numpy python-scipy 

Graphics dependencies

    sudo apt-get install python-opengl pyside

IO dependencies:

    openbabel, pyxdr(grab it from git)
    

Grab the chemlab source from git:

   git clone https://github.com/chemlab/chemlab.git
   
Just add the chemlab directory to the PYTHONPATH in your .bashrc

   export PYTHONPATH=$PYTHONPATH:/path/to/chemlab


Once you're setup you're ready to go to dig in chemlab's features.




