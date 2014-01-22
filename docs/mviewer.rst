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

.. image:: _static/mviewer_screen1.png
    :width: 600px

Let's try how to work with it with some simple tasks.


Distance between two atoms
..........................

How do I find the interatomic distance between two selected atoms?

Chemlab gives you some basic functions to change and retrieve
information of what's currently displaying.

For example, to get the current :class:`~chemlab.core.System` instance
being displayed you can type::

     In: s = current_system()

If you want to know which are the indexes of the atoms currently
selected you can type the following command::
  
    In : selected_atoms()
    Out: array([ 0,  1])

You can also do the reverse, given the indexes you can select two
atoms, the interface will update accordingly::

    select_atoms([0, 1])

To calculate the distance between the selected atoms, we have first to
retrieve their indexes first and then use the System to retrieve their
coordinates. At that point we can use them to find the distance (it's
the norm of the difference between the two coordinates)::

    selected = selected_atoms()
    s = current_system()
    a, b = s.r_array[selected]
    import numpy as np
    distance = np.linalg.norm(a - b)

Changing the appeareance
........................

Chemlab lets you change the appeareance of the things that get
displayed in a really easy way.

For example we can select all the carbon atoms and give them a size of 0.3::

    select_atom_type('C')
    change_radius(0.3)

We can change their color::
  
    change_color(color='black')


Writing your own commands
=========================

This is very important because that's exactly what you're supposed to do.

chemlab has a directory .chemlab in your home. And in this directory
you'll find a __init__.py. Chemlab executes it and reads everything
that is contained.

To access the basic commands you should import::
  
    from chemlab.mviewer.api import *

In this way I've got you set with the basic names that you need. Here
you can import and write your own toolboxes... In pure emacs style you
don't have any constraint.


Loading Data
============

We can start by loading some files in this way::

    load_system()
    load_trajectory()

You can move to a different time and inspect which time is that using
the following command::

    goto_time() 
    current_time()
    current_frame()

Selecting commands
==================

Here we enter in our stateful framework. We can hide elements from the
view. For example we can select all atoms.

The main command to select stuff is select::

    select(atom_type='H')
    select(atoms=[0, 1, 2])
    select(selection=selection) # a selection object

    clear_selection()

You can combine selections by continuing selecting stuff::

  select(atom_type='H', add=True)
  select(formula='H2O')

Each selection routine returns a Selection object, that contains
information on the selection state, so you can use it later::

    selection['atoms']
    [1, 2, 3]
    selection['bonds']
    [1, 2]

You can combine selections::

    sel1.add(sel2)
    sel1.subtract(sel2) # Subtracts another selection
    sel1.intersect(sel2) # Computes the intersection
    
    sel1.invert()
    
To easily retrieve the currently selected atoms and bonds::

    selected_atoms()
    selected_bonds()
    invert_selection()

You can also write your own conveniency routines (the goal is to save
some typing time) like::

   select_water()
   hide_water()

Hiding and Showing
==================
   
Once you have your own selection you can simply type hide

Selection commands will usually work on visible things only unless you write::

    select_all(hidden=True) # Select also hidden

    # How to select hidden only?
    select_all().invert()

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

So we should put this in the file .chemlab/toolboxes/my_selects.py
and we should load this at the chemlab start in the .chemlab/toolboxes/__init__.py::

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
