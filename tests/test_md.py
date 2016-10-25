'''Molecular Dynamics tests with uff'''
from __future__ import print_function
import numpy as np
import pint

from chemlab.core import *
from chemlab.io import datafile
from chemlab.md.analysis import rdf

from chemlab.md.potential import ForceGenerator, InterMolecular, IntraMolecular, to_top
from nose.tools import eq_
from chemlab.md.interactions import Coulomb, LennardJones, TosiFumi
from chemlab.md.ewald import Ewald
from chemlab.utils.pbc import minimum_image
units = pint.UnitRegistry()
c_unit = 1e-19 * units.joule * units.angstrom**6
d_unit = 1e-19 * units.joule * units.angstrom**8

tosi_fumi_spec = {
    ('Li', 'Cl') : {
        "sigma" :  [0.816 * units.angstrom, 1.585 * units.angstrom],
        "q" : [1, -1],
        'valence': [2, 8],
        "C": [0.073 * c_unit, 2.0 * c_unit, 111.0 * c_unit],
        "D": [0.03 * d_unit, 2.4 * d_unit, 223.0 * d_unit],
        "b": 0.338e-12 * units.erg,
        "alpha" : 2.92 / units.angstrom
    },
}

def fix_units(spec):
    spec = spec.copy()
    N_A = units.avogadro_number
    kj_mol = units.kilojoule / units.mole
    spec["sigma"] = [v.to(units.nanometer).magnitude for v in spec["sigma"]]
    spec["C"] = [(N_A * v).to(kj_mol * units.nanometer ** 6).magnitude for v in spec["C"]]
    spec["D"] = [(N_A * v).to(kj_mol * units.nanometer ** 8).magnitude for v in spec["D"]]
    spec["b"] = (N_A * spec["b"]).to(kj_mol).magnitude
    spec["alpha"] = spec["alpha"].to(1 / units.nanometer).magnitude
    
    return spec
    
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
    
    particles1 = [[0, 0, 0]]
    types1 = ["Li"]
    particles2 = [[0.10, 0, 0]]
    types2 = ["Cl"]
    
    tf = TosiFumi({k: fix_units(spec) for k, spec in tosi_fumi_spec.items()})
    result = tf.interaction(particles1, types1, particles2, types2)
    print(result) # should be 1408.55893904
    
ROCKSALT_M = 1.748
WURTZ_M = 1.638

from chemlab.md.energy import F
def madelung(r, M):
    return F * M / r

def rmin(box):
    D = box.r_array[np.newaxis] - box.r_array[:, np.newaxis]
    D = (D**2).sum(axis=-1)**0.5
    return D[np.triu_indices(D.shape[0], 1)].min()
    
def test_ewald():
    particles1 = [[0.0, 0, 0], [0.5, 0.5, 0.5]]
    types1 = ["Li", "Cl"]
    box = [1.0, 1.0, 1.0]
    
    li = Molecule([Atom('Li', [0, 0, 0], name='Li+')])
    cl = Molecule([Atom('Cl', [0, 0, 0], name='Cl-')])

    cell_par = 2.0
    rocksalt = crystal([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]], # Fractional Positions
            [li, cl], # Molecules
            225, # Space Group
            cellpar = [cell_par, cell_par, cell_par, 90, 90, 90], # unit cell parameters
            repetitions = [1, 1, 1]) # unit cell repetitions in each direction
    
    particles1 = rocksalt.r_array
    types1 = rocksalt.type_array.astype("S2")
    box = np.diagonal(rocksalt.box_vectors)
    
    # for k_max in (2, 3, 4, 5, 6):
    rcut = cell_par * 4
    ewald = Ewald({"Li": 1, "Cl": -1}, rcut=rcut, alpha=(3.6/0.9)**0.5, kmax=10)
    result = ewald.real(particles1, types1, particles1, types1, box)

    print("Real", result)
    result = ewald.reciprocal(particles1, types1, particles1, types1, box)
    print("Reciprocal", result)
    print("Whole", ewald.interaction(particles1, types1, particles1, types1, box) / 2)

    print("Madelung", madelung(rmin(rocksalt), ROCKSALT_M)/2)
    
def test_ewald_wurtzite():
    particles1 = [[0.0, 0, 0], [0.5, 0.5, 0.5]]
    types1 = ["Li", "Cl"]
    box = [1.0, 1.0, 1.0]
    
    li = Molecule([Atom('Li', [0, 0, 0], name='Li+')])
    cl = Molecule([Atom('Cl', [0, 0, 0], name='Cl-')])

    cell_param = 0.45
    wurtz = crystal([[2/3., 1/3., 0.0], [2/3., 1/3., 3/8.]], # Fractional Positions
                [li,  cl], # Molecules
                186, # Space Group
                cellpar = [cell_param * 1., cell_param * 1., cell_param * 2. * (2/3.)**0.5, 90, 90, 120], # unit cell parameters
                repetitions = [1, 1, 1]) # unit cell repetitions in each direction
    
    # Volume is the same
    a, b, c = wurtz.box_vectors
    # 
    # print("Volume 1", np.dot(a, np.cross(b, c)))
    # print("Volume 2", np.prod(np.diagonal(wurtz.box_vectors)))

    # straight_box = np.diag(np.diagonal(wurtz.box_vectors))
    # wurtz.box_vectors = straight_box
    # wurtz.r_array = minimum_image(wurtz.r_array + cell_param/2, np.diagonal(wurtz.box_vectors))

    particles1 = wurtz.r_array
    types1 = wurtz.type_array.astype("S2")
    # box = np.diagonal(wurtz.box_vectors)
    box = wurtz.box_vectors
    
    # for k_max in (2, 3, 4, 5, 6):
    rcut = cell_param * 4
    ewald = Ewald({"Li": 1, "Cl": -1}, rcut=rcut, alpha=(3.6/0.9)**0.5, kmax=10)
    result = ewald.real(particles1, types1, particles1, types1, box)
    
    
    # print("Real", result)
    # result = ewald.reciprocal(particles1, types1, particles1, types1, box)
    # print("Reciprocal", result)
    # print("Dipole", ewald.dipole_correction(particles1, types1, box) / 4)
    print("Whole", ewald.interaction(particles1, types1, particles1, types1, box) / 2)
    print("Madelung", madelung(rmin(wurtz), WURTZ_M)/2)
    
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
