'''Mol2 file handler
Contributed by @jaimergp
'''
import numpy as np

from .base import IOHandler
from ...core import Molecule


class Mol2IO(IOHandler):

    '''Reader for Mol2 molfile
    (Specs: http://www.tripos.com/data/support/mol2.pdf)

    **Features**

    .. method:: read("molecule")

        Read the molecule in a :py:class:`~chemlab.core.Molecule`
        instance.

    '''

    can_read = ['molecule']

    def read(self, feature):
        self.check_feature(feature, "read")

        if feature == 'molecule':
            # string = self.fd.read().decode('utf-8')
            return self.parse_mol2()

    def parse_mol2(self):
        # Flags
        mol_section, atom_section, bond_section = False, False, False
        moldata, coords, types, bonds, bond_types = [], [], [], [], []
        for line in self.fd:
            line = line.decode('utf-8')
            if line.startswith('#'):
                continue
            elif line.startswith('@<TRIPOS>MOLECULE'):
                mol_section, atom_section, bond_section = True, False, False
                continue
            elif line.startswith('@<TRIPOS>ATOM'):
                mol_section, atom_section, bond_section = False, True, False
                continue
            elif line.startswith('@<TRIPOS>BOND'):
                mol_section, atom_section, bond_section = False, False, True
                continue
            elif line.startswith('@<TRIPOS>'):
                break

            if mol_section:
                moldata.append(line)
                continue
            elif atom_section:
                atom = line.split()
                types.append(atom[5].split('.')[0])
                coords.append([float(x) for x in atom[2:5]])
                continue
            elif bond_section:
                bond = line.split()
                bonds.append([int(b) for b in bond[1:3]])
                try:
                    bond_types.append(int(bond[3]))
                except ValueError:
                    bond_types.append(1)

        # Molecule data
        # n_atoms, n_bonds, n_subst, n_feat, n_sets = moldata[1].split()

        mol = Molecule.from_arrays(r_array=np.array(coords) / 10,  # to nm
                                   type_array=np.array(types))
        mol.bonds = np.array(bonds) - 1
        mol.bond_orders = np.array(bond_types)
        mol.name = moldata[0]

        return mol
