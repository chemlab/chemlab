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

1) Interatomic distance
2) Change bond and atom appeareance
3) Change colors (select_atoms + change_color)
4) Scale atoms

