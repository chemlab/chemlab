============================
The chemlab molecular viewer
============================

The molecular viewer sets a new standard and a new way of interacting,
editing and analyzing data. Common molecular viewers lacks an easy way
to extend while the chemlab phylosophy everybody should be able to
write a simple plugin. This is because there are so many applications
in chemistry and physics and customizing is the true way.

At the moment the chemlab molecular viewer is a prototype. All is
available is a command line interface that lets you type commands and
interact with the viewer in a pretty easy way. From that, in future
releases it will be possible to modify the user interface and build
interactive tools also for selecting certain areas etc. It's gonna be
good. A LOT

Let's try a small tutorial introduction:

You start chemlab mview. download a sample molecule from the web::

    download_molecule('aspirine')

By clicking the atoms it will select the atoms. To retrieve the selected atoms yo ucan type::
  
    selected_atoms()
    [0, 1]

Tasks that we'll try to accomplish:

How to find interatomic distance?

::
    distance_between_atoms(0, 1) # Between the first two atoms
    distance_between_atoms()     # Interactive, between the two 
                                 # currently selected atoms


How to change bond and atom appeareance

We can change their size::
    scale(scale_factor=2.0)

We can change their color::
    change_color(color='green')

We can globally change the color scheme (which is a dictionary)::
    change_color_scheme(someotherscheme)

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

    sel1.and(sel2)
    sel1.sub(sel2) # Subtracts another selection
    
    sel1.or(sel2)
    sel1.xor(sel2)
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

Cookbook
========

You have a protein solvated in water, you want to remove the water and
make it big balls::

    $ chemlab mview prot.pdb

    
Let's solvate a protein in water::

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
