import re
import numpy as np

from .base import IOHandler, FeatureNotAvailable

from .gro_map import gro_to_cl

from ...core import System

from ...utils.formula import make_formula
from ...db import ChemlabDB


symbol_list = ChemlabDB().get('data', 'symbols')
symbol_list = [s.lower() for s in symbol_list]


class GromacsIO(IOHandler):
    '''Handler for .gro file format. Example at
    http://manual.gromacs.org/online/gro.html.

    **Features**

    .. method:: read("system")

       Read the gro file and return a :py:class:`~chemlab.core.System`
       instance. It also add the following exporting informations:

       groname: The molecule names indicated in the gro file. This is
            added to each entry of `System.mol_export`.

       grotype: The atom names as indicated in the gro file. This is
            added to each entry of `System.atom_export_array`.

    .. method:: write("system", syst)

       Write the *syst* :py:class:`~chemlab.core.System` instance to
       disk. The export arrays should have the *groname* and *grotype*
       entries as specified in the ``read("system")`` method.

    **Example**

    Export informations for water SPC::

         Molecule([
                   Atom('O', [0.0, 0.0, 0.0], export={'grotype': 'OW'}),
                   Atom('H', [0.1, 0.0, 0.0], export={'grotype': 'HW1'}),
                   Atom('H', [-0.033, 0.094, 0.0],export={'grotype':'HW2'})],
                 export={'groname': 'SOL'})

    '''

    can_read = ['system']
    can_write = ['system']

    def read(self, feature):
        super(GromacsIO, self).read(feature)
        
        if feature == 'system':
            lines = self.fd.readlines()
            lines = [line.decode('utf-8') for line in lines]
            return parse_gro_lines(lines)

    def write(self, feature, sys):
        super(GromacsIO, self).write(feature, sys)
        
        if feature == 'system':
            write_gro(sys, self.fd)


def parse_gro_lines(lines):
    '''Reusable parsing'''
    title = lines.pop(0)
    natoms = int(lines.pop(0))
    atomlist = []

    # I need r_array, type_array
    datalist = []
    for l in lines:
        fields = l.split()
        line_length = len(l)

        if line_length in (45, 46, 69, 70):
            #Only positions are provided
            molidx = int(l[0:5])
            moltyp = l[5:10].strip()
            attyp = l[10:15].strip()
            atidx = int(l[15:20])
            rx = float(l[20:28])
            ry = float(l[28:36])
            rz = float(l[36:44])

            hasvel = False
            if line_length == 69:
                hasvel = True
                # Provide velocities
                vx = float(l[44:52])
                vy = float(l[52:60])
                vz = float(l[60:68])

            # Do I have to convert back the atom types, probably yes???
            #if attyp.lower() not in symbol_list:
            #    attyp = gro_to_cl[attyp]
            datalist.append((molidx, moltyp, attyp, rx, ry, rz))
        else:
            # This is the box size
            stuff  = [float(f) for f in fields]
            a,b,c = stuff[0], stuff[1], stuff[2]
            box_vectors = np.array([[a, 0, 0], [0, b, 0], [0, 0, c]])
            break

    dataarr = np.array(datalist,
                       dtype=np.dtype([('f0', int), ('f1', object),
                                       ('f2', object), ('f3', np.float64),
                                       ('f4', np.float64), ('f5', np.float64)]
                                      )
                       )

    # Molecule indices: unique elements in molidx
    mol_id, mol_indices = np.unique(dataarr['f0'], return_index=True)
    
    maps = {('atom', 'molecule') : dataarr['f0'] - 1}
    
    r_array = np.vstack([dataarr['f3'],
                         dataarr['f4'],
                         dataarr['f5']]).transpose()
    grotype_array = dataarr['f2']
    grores_array = dataarr['f1'][mol_indices]
    
    molecule_export = np.array([dict(groname=g)
                           for g in dataarr['f1'][mol_indices]])
    atom_export = np.array([dict(grotype=g) for g in grotype_array])

    # Gromacs Defaults to Unknown Atom type
    
    # We need to parse the gromacs type in some way...
    # grotype_array = [re.sub('[0-9+-]+$', '', g) for g in grotype_array]
    type_array = np.array([gro_to_cl.get(re.sub('[0-9+-]+$','', g), "Unknown") for g in grotype_array])

    # Molecular Formula Arrays
    mol_formula = []
    end = len(r_array)
    for i, _ in enumerate(mol_indices):
        s = mol_indices[i]
        e = mol_indices[i+1] if i+1 < len(mol_indices) else end
        mol_formula.append(make_formula(type_array[s:e]))

    mol_formula = np.array(mol_formula)

    # n_mol, n_at
    sys = System.from_arrays(r_array=r_array,
                             maps=maps,
                             type_array=type_array,
                             atom_name=grotype_array,
                             atom_export=atom_export,
                             molecule_export=molecule_export,
                             molecule_name=grores_array,
                             box_vectors=box_vectors)
    return sys


def write_gro(sys, fd):
    lines = []
    lines.append('Generated by chemlab')
    lines.append('{:>5}'.format(sys.n_atoms))

    at_n = 0
    # Residue Number
    for i in range(sys.n_mol):
        res_n = i + 1

        res_name = sys.molecule_name[i]
        # try:
        #     res_name = sys.molecule_export[i]['groname']
        # except KeyError:
        #     raise Exception('Gromacs exporter need the '
        #                     'residue name as groname')

        for j in range(sys.mol_n_atoms[i]):
            offset = sys.mol_indices[i]
            
            at_name = sys.atom_name[offset + j]
            # try:
            #     at_name = sys.atom_export[offset+j]['grotype']
            # except KeyError:
            #     raise Exception('Gromacs exporter needs'
            #                     'the atom type as grotype')

            at_n += 1
            x, y, z = sys.r_array[offset+j]

            lines.append('{:>5}{:<5}{:>5}{:>5}{:>8.3f}{:>8.3f}{:>8.3f}'
                         .format(res_n % 99999, res_name,
                                 at_name, at_n % 99999, x, y, z))

    if sys.box_vectors is None:
        raise Exception('Gromacs exporter need box_vectors'
                        'information System.box_vectors')

    lines.append('{:>10.5f}{:>10.5f}{:>10.5f}{:>10.5f}{:>10.5f}{:>10.5f}{:>10.5f}{:>10.5f}{:>10.5f}'.format(sys.box_vectors[0, 0],
                                                      sys.box_vectors[1, 1],
                                                      sys.box_vectors[2, 2],
                                                      sys.box_vectors[0, 1],
                                                      sys.box_vectors[0, 2],
                                                      sys.box_vectors[1, 0],
                                                      sys.box_vectors[1, 2],
                                                      sys.box_vectors[2, 0],
                                                      sys.box_vectors[2, 1]))

    #for line in lines:
    #    print line

    lines = [l + '\n' for l in lines]

    fd.writelines(lines)
