"""Topology handling in gromacs"""
from ..db import ChemlabDB
from ..core import System, Molecule, Atom
from ..table import atomic_no, atomic_weight

from .energy import lorentz_berthelot as combine_lorentz_berthelot

import itertools
import time
import datetime
from itertools import combinations, combinations_with_replacement
from collections import OrderedDict

import numpy as np
def line(*args, **kwargs):
    just = kwargs.get("just", "left")
    if just == "right":
        return ' '.join(str(a).rjust(10) for a in args) + '\n'
    if just == "left":
        return ' '.join(str(a).ljust(10) for a in args) + '\n'
    else:
        raise ValueError('just must be right or left')


def comment(*args):
    return ';' + line(*args)


class ChargedLJ(object):

    def __init__(self, name, q, type, sigma, eps):
        self.name = name
        self.q = q
        self.type = type
        self.sigma = sigma
        self.eps = eps

    @property
    def c6(self):
        return 4.0 * self.eps * self.sigma ** 6

    @property
    def c12(self):
        return 4.0 * self.eps * self.sigma ** 12


class InterMolecular(object):

    def __init__(self, type='lj'):
        self.particles = {}
        self.special_pairs = {}
        self.type = type

    @classmethod
    def from_dict(cls, data):
        self = cls()
        for name, atomspec in data.items():
            particle = ChargedLJ(name, atomspec['q'], atomspec[
                                 'type'], atomspec['sigma'], atomspec['eps'])
            self.particles[name] = particle

        return self

    def pair_interaction(self, a, b):
        i, j = self.particles[a], self.particles[b]

        if (a, b) in self.special_pairs:
            params = self.special_pairs[a, b]
        else:
            params = {}

        if self.type == 'lj':
            sigma, eps = combine_lorentz_berthelot(
                i.sigma, j.sigma, i.eps, j.eps)
            return PairInteraction((i, j), sigma, eps)
        elif self.type == 'custom':
            # We expect coulomb, dispersion, repulsion
            coulomb = params['coulomb']
            dispersion = params['dispersion']
            repulsion = params['repulsion']
            return CustomPairInteraction((i, j), coulomb, dispersion, repulsion)
        else:
            raise ValueError("Type not recognized")


class PairInteraction:

    def __init__(self, pair, sigma=None, eps=None):
        self.pair = pair
        self.sigma, self.eps = combine_lorentz_berthelot(pair[0].sigma, pair[1].sigma, pair[0].eps, pair[1].eps)

    @property
    def c6(self):
        return 4.0 * self.eps * self.sigma ** 6

    @property
    def c12(self):
        return 4.0 * self.eps * self.sigma ** 12

    def f(self, x):
        return 1.0/x
        
    def g(self, x):
        return - self.c6 * (1/x**6)
        
    def h(self, x):
        return self.c12 * (1/x**12)
class CustomParticle:

    def __init__(self, name, type, q, params):
        self.name = name
        self.type = type
        self.params = params
        self.q = q

from scipy.misc import derivative

class CustomPairInteraction:

    def __init__(self, pair, coulomb, dispersion, repulsion):
        '''Define a custom pair interaction. func is a python function that
        takes an array of x values and returns an array of potential values'''

        self.pair = pair
        self.coulomb = coulomb
        self.dispersion = dispersion
        self.repulsion = repulsion

    def f(self, x):
        return self.coulomb(x, self.pair[0].params, self.pair[1].params)
    
    def df(self, x):
        return derivative(self.f, x, dx=1e-10)
    
    def g(self, x):
        return self.dispersion(x, self.pair[0].params, self.pair[1].params)
    
    def dg(self, x):
        return derivative(self.g, x, dx=1e-10)

    def h(self, x):
        return self.repulsion(x, self.pair[0].params, self.pair[1].params)
    
    def dh(self, x):
        return derivative(self.h, x, dx=1e-10)
        

class MolecularConstraints:

    def __init__(self, name, atoms, bonds, angles, dihedrals):
        self.atoms = atoms
        self.name = name
        self.bonds = bonds
        self.angles = angles
        self.dihedrals = dihedrals


class HarmonicConstraint:

    def __init__(self, between, r, k):
        self.between = between
        self.r = r
        self.k = k


class HarmonicAngleConstraint:

    def __init__(self, between, theta, k):
        self.between = between
        self.theta = theta
        self.k = k


class IntraMolecular(object):

    def __init__(self):
        self.molecules = {}

    @classmethod
    def from_dict(cls, data):
        self = cls()
        for name, molspec in data.items():
            if 'bonds' in molspec:
                bonds = [HarmonicConstraint(b['between'], b['r'], b['k'])
                         for b in molspec['bonds']]
            else:
                bonds = []

            if 'angles' in molspec:
                angles = [HarmonicAngleConstraint(b['between'], b['theta'], b['k'])
                          for b in molspec['angles']]
            else:
                angles = []

            cst = MolecularConstraints(
                name, molspec['atoms'], bonds, angles, [])
            self.molecules[name] = cst

        return self


class Potential(object):

    def __init__(self, nonbonded, bonded):
        self.intermolecular = nonbonded
        self.intramolecular = bonded


class ForceGenerator(object):

    def __init__(self, spec):
        self.intermolecular = InterMolecular.from_dict(spec['nonbonded'])
        self.intramolecular = IntraMolecular.from_dict(spec['bonded'])


def to_table(custom_interaction, cutoff, precision='double'):
    if precision == 'single':
        step = 0.002
    if precision == 'double':
        step = 0.0005
    else:
        raise ValueError("Precision can be either single or double")
    
    r = np.arange(0.0, 1 + cutoff + 2*step, step)
    f = custom_interaction.f(r)
    df = custom_interaction.df(r)
    
    g = custom_interaction.g(r)
    dg = custom_interaction.dg(r)
    
    h = custom_interaction.h(r)
    dh = custom_interaction.dh(r)
    
    columns = [r, f, -df, g, -dg, h, -dh]
    
    rows = np.array(columns).T
    rows[0] = 0.0
    return '\n'.join(' '.join("%.8E" % n for n in row) for row in rows)

def to_top(system, potential):
    molecules = [system.subentity(Molecule, i)
                 for i in range(system.dimensions['molecule'])]
    unique_molecules = OrderedDict()
    [unique_molecules.__setitem__(m.molecule_name, m) for m in molecules]

    unique_atoms = OrderedDict()
    for m in unique_molecules.values():
        for a in [m.subentity(Atom, i) for i in range(m.dimensions['atom'])]:
            unique_atoms[a.atom_name] = a
    # Defaults section
    r = ''
    r += comment('Generated by chemlab ' +
                 datetime.datetime
                 .fromtimestamp(time.time())
                 .strftime('%Y-%m-%d %H:%M:%S'))

    r += line('[ defaults ]')
    r += comment('nbfunc', 'comb-rule', 'gen-pairs', 'fudgeL', 'fudgeQQ')
    r += line(1, 1, "yes", 0.5, 0.5)
    r += line()

    # Non bonded interactions
    r += line('[ atomtypes ]')
    r += comment('name', 'atom_type', 'mass', 'charge', 'ptype', 'C', 'A')
    name_to_type = {}

    for atom in unique_atoms:
        # potential.intermolecular.particles
        particle = potential.intermolecular.particles[atom]
        if isinstance(particle, ChargedLJ):
            r += line(particle.name, particle.type, atomic_no(particle.type), atomic_weight(particle.type),
                      particle.q, 'A', particle.c6, particle.c12)
        elif isinstance(particle, CustomParticle):
            r += line(particle.name, particle.type, atomic_no(particle.type), atomic_weight(particle.type),
                      particle.q, 'A', 1.0, 1.0)
        else:
            raise ValueError("unknown particle type {}".format(particle))

        name_to_type[particle.name] = particle.type

    r += line()
    r += line('[ nonbondparams ]')
    r += comment('i', 'j', 'func', 'V', 'W')

    # We override gromacs with our own rules
    for atom1, atom2 in combinations_with_replacement(unique_atoms, 2):
        # potential.intermolecular.pairs:
        pair = potential.intermolecular.pair_interaction(atom1, atom2)

        if isinstance(pair, PairInteraction):
            r += line(pair.pair[0].name,
                      pair.pair[1].name,
                      1,  # Combination rule 1 = lorentz-berthelot
                      pair.c6,
                      pair.c12)

        elif isinstance(pair, CustomPairInteraction):
            r += line(pair.pair[0].name,
                      pair.pair[1].name, 1, 1.0, 1.0)

        else:
            raise ValueError("Wrong pair interaction {}".format(pair))

    r += line()

    for molecule_name in unique_molecules:
        # print potential.intramolecular.molecules
        molecule = potential.intramolecular.molecules[molecule_name]

        r += line('[ moleculetype ]')
        r += comment('name', 'nbexcl')
        r += line(molecule.name, 2)
        r += line()
        # Atoms directive...
        r += line('[ atoms ]', just="left")
        r += comment('nr', 'type', 'resnr', 'residue',
                     'atom', 'cgnr', 'charge', 'mass')
        for i, t in enumerate(molecule.atoms):
            p = potential.intermolecular.particles[t]
            r += line(i + 1, t, 1, molecule.name, t, 1, p.q)
        #     1  O          1    SOL     OW      1      -0.8476
        r += line()

        # Bonds directive...
        if molecule.bonds:
            r += line('[ bonds ]', just="left")
            r += comment('i', 'j', 'funct', 'length', 'force.c.')
            for b in molecule.bonds:
                r += line(b.between[0] + 1, b.between[1] + 1, 1, b.r, b.k)
            r += line()

        # Angle directive...
        if molecule.angles:
            r += line('[ angles ]', just="left")
            r += comment('i', 'j', 'k', 'funct', 'angle', 'force.c.')
            for ang in molecule.angles:
                r += line(ang.between[0] + 1,
                          ang.between[1] + 1,
                          ang.between[2] + 1, 1, ang.theta, ang.k)
            r += line()

        # Create dihedrals
        for ang in molecule.dihedrals:
            r += line(ang.between[0] + 1,
                      ang.between[1] + 1,
                      ang.between[2] + 1, 1, ang.theta, ang.k)
        r += line()

    # System
    r += line('[ system ]')
    r += line('flying pandas')
    r += line()

    r += line('[ molecules ]')
    counter = 0
    current = -1
    mollist = []
    for t in system.molecule_name:
        if t != current:
            mollist.append((current, counter))
            current = t
            counter = 0
        counter += 1

    mollist.append((current, counter))
    mollist.pop(0)

    for mol, counter in mollist:
        r += line(mol, counter)

    return r


def from_top(topfile):
    topfile.read()

    # atom_types
    # pair_interactions -> system-wide (they are combined for all molecules)
    # bond_interactions -> relative to each molecule
    # angle_interactions -> relative to each molecule

    # number of molecules -> relative only to the system, but this is a flaw of
    # the top format, we don't read that
