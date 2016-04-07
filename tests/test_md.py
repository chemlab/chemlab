'''Molecular Dynamics tests with uff'''
import numpy as np

from chemlab.core import *
from chemlab.io import datafile
from chemlab.md.analysis import rdf

from chemlab.md.potential import ForceGenerator, InterMolecular, IntraMolecular, to_top
from nose.tools import eq_
from chemlab.md.interactions import Coulomb, LennardJones

def test_energy_calc():
    
    # How do you calculate energy?
    particles1 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    types1 = ["Li", "Cl", "Cl"]
    
    particles2 = [[1, 1, 1]]
    types2 = ["Li"]
    
    coulomb = Coulomb({"Li" : 1, "Cl": -1})
    result = coulomb.interaction(particles1, types1, particles2, types2)
    print(result)
    
    lj = LennardJones({ "Li": { "sigma": 0.2, "eps": 0.3 },
                        "Cl": { "sigma": 0.2, "eps": 0.3 }})
    
    result = lj.interaction(particles1, types1, particles2, types2)
    print(result)

def test_energy_calc_speed():
    lj = LennardJones({ "Li": { "sigma": 0.2, "eps": 0.3 },
                        "Cl": { "sigma": 0.2, "eps": 0.3 }})
    particles1 = np.random.rand(10000, 3)
    particles2 = np.random.rand(10000, 3)
    types1 = ["Li"] * 1000 
    types2 = ["Cl"] * 1000
    
    result = lj.interaction(particles1, types1, particles2, types2)
    # print(result)

    
def test_from_dict():
    # Define a new potential, the format is python dictionary or json
    spec = {
        "nonbonded" :  {"Na" : {"q" : 1, "sigma": 0.2, "eps": 0.3, "type": "Na"},
                        "Cl" : {"q" : -1, "sigma": 0.2, "eps": 0.3, "type": "Cl"},
                        "OW" : {"q" : 1, "sigma": 0.2, "eps": 0.3, "type": "O"},
                        "HW1" : {"q" : 1, "sigma": 0.2, "eps": 0.3, "type": "H"},
                        "HW2" : {"q" : 1, "sigma": 0.2, "eps": 0.3, "type": "H"}},

        "bonded" : {'SOL' : { 'atoms': ['OW', 'HW1', 'HW2'], 
                              'bonds': [{ 'between': (0, 1), 'r' : 0.2, 'k': 0.1 }, 
                                        { 'between': (0, 1), 'r' : 0.2, 'k': 0.1 }],
                              'angles': [{'between': (1, 0, 2), 'theta' : 90, 'k': 0.1}]
                            },
                    'NA' :  { 'atoms' : ['Na'] },
                    'CL' :  { 'atoms' : ['Cl'] },
                   }
    }
    
    na = Molecule.from_arrays(type_array=['Na'], molecule_name='NA', atom_name=['Na'])
    cl = Molecule.from_arrays(type_array=['Cl'], molecule_name='CL', atom_name=['Cl'])
    water = Molecule.from_arrays(type_array=['O', 'H', 'H'], 
                                 molecule_name='SOL',
                                 atom_name=['OW', 'HW1', 'HW2'],
                                 bonds=[[0, 1], [0, 2]])

    s = System([na, na, cl, cl, water, water])
    p = ForceGenerator(spec)
    
    to_top(s, p)

def test_rdf():
    system = datafile("tests/data/rdf/cry.gro").read('system')
    # Fix for this particular system water.gro
    #system.r_array += system.box_vectors[0,0]/2
    
    gro_rdf = np.loadtxt("tests/data/rdf/rdf.xvg", skiprows=13,unpack=True)
    #nbins = len(gro_rdf[0])
    size = system.box_vectors[0,0]/2
    
    rdf_ =rdf(system.r_array[system.type_array == 'Cl'],
              system.r_array[system.type_array == 'Li'],
              binsize=0.002,
              cutoff=size,
              periodic = system.box_vectors)
    
    mse = ((rdf_[1] - gro_rdf[1, :-2])**2).mean()
    assert mse < 1.0
