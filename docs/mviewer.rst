============================
The chemlab molecular viewer
============================

The Chemlab molecular viewer sets a new standard and a new way of
interacting, editing and analyzing data. The chemlab philosophy is
that the program should be really easy to extend, without sacrificing
any power. There are so many applications in chemistry and physics and
the user can't be limited to the built-in functionalities of the program.

Right now the chemlab molecular viewer consist in a viewer and a
shell. You can type commands and the changes will appear
interactively. 

Quick Start
===========

You can start the chemlab molecular viewer by typing::

    chemlab mview

This will load the user interface consisting of the viewer, and an
IPython shell.

.. image:: _static/mviewer_screen1.png
    :width: 600px

You can start typinc commands in the IPython shell and changes will
appear in the upper viewer. For example downloading a molecule from
the web is really easy with the command download_molecule::

   download_molecule('aspirine')

By clicking the atoms it will select the atoms. The selection effect
is a white glow.

.. image:: _static/mviewer_screen2.png
    :width: 600px

Let's try how to work with it with some simple tasks.


Distance between two atoms
..........................

How do I find the interatomic distance between two selected atoms?

Chemlab gives you some basic functions to change and retrieve
information of what's currently displaying.

For example, to get the current :class:`~chemlab.core.System` instance
being displayed you can type::

     current_system()

If you want to know which are the indexes of the atoms currently
selected you can type the following command::
  
    selected_atoms()
    # Out: array([ 0,  1])

You can also do the reverse, given the indexes you can select two
atoms, the interface will update accordingly::

    select_atoms([0, 1])

To calculate the distance between the selected atoms, we have to first
retrieve their indexes and then use the System to retrieve their
coordinates. At that point we can use them to find the distance (it's
the norm of the difference between the two coordinates)::

    selected = selected_atoms()
    s = current_system()
    a, b = s.r_array[selected]
    import numpy as np
    distance = np.linalg.norm(a - b)

Changing the appeareance
........................

Chemlab lets you change the appeareance of the objects in a really
easy way.

For example we can select all the carbon atoms using the
select_atom_type function and give them a size of 0.3 with the function change_radius, that operates on the current selection::

    select_atom_type('C')
    change_radius(0.3)

Similarly, we can change their color with the change_color function::
  
    change_color(color='black')

For a complete reference of the commands refer to the :doc:`api/chemlab.mviewer.toolboxes`.

Writing your own commands
=========================

The built-in commands provide a quick and easy way to operate on your
molecules and they provide basic functionality. The true power of chemlab
relies in the possibility to write and load your commands using the power
and simplicity of Python.

For example we can write a command that calculates automatically the
distance between two selected atoms. We can open a file *utils.py* and
put the following code in it::

  import numpy as np
  
  def distance():
     sel = selected_atoms()
     if len(sel) != 2:
         print("Only two atoms must be selected")
	 return
     else:
         a, b = current_system().r_array[sel]
	 return np.linalg.norm(b - a)

How can we access this function from a chemlab session? 

The chemlab shell is just a regular Python shell, so one solution will
be to simply add the directory to your PYTHONPATH and import it manually.

However, chemlab provides an init file that lets you write some code
that's called an initialization time, saving you quite a bit of typing
time.

The file is stored in your home directory
.chemlab/scripts/__init__.py. For example, we can add the following
line to automatically load the command "distance", after putting the file utils.py in the directory .chemlab/scripts/::
  
  from .utils import distance

In this way you can easily write and hook in a lot of extensions, if you write something useful (You will!) just attach your code on the chemlab github page https://github.com/chemlab/chemlab/issues?labels=extension&milestone=&state=open

Loading Data
============

The Chemlab molecular viewer provides quite handy function to load
some data into it::

  load_system("file.gro")
  load_molecule("file.cml")

You can also download the molecule from a web database by its common
name::
  
  download_molecule('aspirine')

Or you can also download and open a file from a remote location using
directly its URL::
  
  load_remote_system('https://raw.github.com/chemlab/chemlab-testdata/master/naclwater.gro')
  load_remote_molecule('https://raw.github.com/chemlab/chemlab-testdata/master/benzene.mol')

Loading Trajectories
....................

Chemlab supports the loading of trajectory files (for example the xtc
files from GROMACS). After you load a system you can attach some
trajectory data with load_trajectory or load_remote_trajectory::

  load_system('water.gro')
  load_trajectory("traj.xtc")
  
We can run a small test using the test files from chemlab::

  load_remote_system('https://raw.github.com/chemlab/chemlab-testdata/master/water.gro')
  load_remote_trajectory('https://github.com/chemlab/chemlab-testdata/raw/master/trajout.xtc')

A series of commands will appear, and you can move through the
trajectory by dragging the bar or the Play/Stop button.

You can also move programmatically using the function goto_time and
goto_frame and inspect with the functions current_time and current_frame

Selections
==========

In Chemlab you usually operate on the selected atoms, bonds or in
general objects.

You can use the built-in functions to select according to various
types::

  select_atoms([0, 1, 2])
  select_atom_type('Na')
  select_molecules('H2O')
  select_all()
  select_within([0, 1], 0.2)
  
You can also act on the selection in different ways::

  invert_selection()
  clear_selection()

Each selection routine returns Selection object, that contains
information on the selection state, so you can use it later::

  select_atoms([0, 1, 2])
  Selection([0, 1, 2], tot=6)

The Selection objects have an API to be combined. For example if you
can select Na and Cl atoms you can do in this way, using the function
select_selection::

  na_at = select_atoms('Na')
  cl_at = select_atoms('Cl')
  select_selection({'atoms' : na_at.add(cl_at)})
    
You can retrieve retrieve the currently selected atoms and bonds in
this way, they will return a set of indices of the selected atoms and
bonds::

  selected_atoms()
  selected_bonds()

Hiding and Showing
==================
   
Sometimes you want to hide certain objects from the current view to
remove clutter. For example if you want to select all the water
molecules and hide them::

  select_molecules('H2O')
  hide()

There's also a conveniency function to do this::

  hide_water()
  
You can also select hidden objects and show them::

  select_hidden()
  show()


Extending
=========

Say we want to get a method that selects the atoms within a certain
range from one::

    def select_within(atom, radius):
        pass

The thing is pretty easy to implement, we first need to do this::

  s = current_system()
  clear_selection()
  nbs = periodic_distance(s.r_array[atom], s.r_array) < radius
  nbs = nbs.nonzero()[0] # we get the actual neighbour indices
  return select(ids=nbs)

So we should put this in the file .chemlab/toolboxes/my_selects.py and
we should load this at the chemlab start in the
.chemlab/toolboxes/__init__.py::

  from my_selects import *

Now when you start chemlab this thing will be made available immediately.

Cookbook
========

You have a protein solvated in water, you want to remove the water and
make it big balls::

    $ chemlab mview prot.pdb

Let's solvate a protein in water::

    from chemlab.mviewer.toolboxes.core import *

    load_system('prot.pdb')
    # Now we get the current system and add the solvation thing as usual
    s = current_system()
    # I'll make a box like this
    wat_box = random_lattice_box([wat], 1000, [7, 7, 7])
    solv_box = merge_systems(wat_box, s)
    
    # We show it again!
    display_system(solv_box)

We can wrap it into a toolbox::
  
    solvate()
    save_system("out.gro")
