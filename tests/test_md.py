'''Molecular Dynamics tests with uff'''
import numpy as np

from chemlab.core import *
from chemlab.md.analysis import rdf

from chemlab.md.potential import ForceGenerator, InterMolecular, IntraMolecular, to_top
from nose.tools import eq_

stretch_k_ij = {
    ('H_','H_') : 1.0
}

bond_r_ij = {
    ('H_','H_') : 0.354 + 0.354,
}

def calculate_energy(r_array, mdtype_array, bonds):
    r_ij = bond_r_ij
    k_ij = stretch_k_ij
    
    en = 0
    # Bond stretching part
    for i_1, i_2 in bonds:
        t_1 = mdtype_array[i_1]
        t_2 = mdtype_array[i_2]
        r = np.linalg.norm(r_array[i_1] - r_array[i_2])
        en += 0.5 * k_ij[(t_1, t_2)] * (r - r_ij[(t_1, t_2)])
    
    return en

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
    
    na = Molecule.from_arrays(type_array=['Na'], molecule_name='NA')
    cl = Molecule.from_arrays(type_array=['Cl'], molecule_name='CL')
    water = Molecule.from_arrays(type_array=['O', 'H', 'H'], 
                                 molecule_name='SOL',
                                 bonds=[[0, 1], [0, 2]])

    s = System([na, na, cl, cl, water, water])
    p = ForceGenerator(spec)
    
    print(p.intermolecular.particles)
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
