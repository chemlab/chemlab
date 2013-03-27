==========================
Using GROMACS with chemlab
==========================

TODO
..
  GROMACS is one of the most used packages for molecular simulations,
  chemlab can provide a modern and intuitive interface for input and
  analysis purposes.  To illustrate the concepts we'll perform a
  simulation of liquid water.
   
  In order to run a minimum simulation GROMACS requires to know some
  basic properties of our system. First of all, we have to provide
  gromacs the dimensions and the positions of our particles (coordinate
  file), information about the connectivity between particles along with
  the intra-molecular interactions (topology file). Once we set the
  propertiees of the system all we need to do is performing a
  simulation, and this will require us to give parameters on how we want
  to make the system evolve (mdp parameter file).
   
  chemlab effectively help us to generate in a flexible way a coordinate file for our system, there are multiple ways of doing that, we will just pick one. Read the comments::
   
      from chemla.core import System
      from chemlab.graphics import display_system
      from chemlab.data.moldb import water
      
      
      display_system(s)
    
