# Adapted from ASE https://wiki.fysik.dtu.dk/ase/
#
#

# Copyright (C) 2010, Jesper Friis
# (see accompanying license files for details).

"""
A module for chemlab for simple creation of crystalline structures from
knowledge of the space group.

"""

import numpy as np
from collections import Counter

from .spacegroup import Spacegroup
from ..system import System
from .cell import cellpar_to_cell



__all__ = ['crystal']


def crystal(positions, molecules, group,
            cellpar=[1.0, 1.0, 1.0, 90, 90, 90], repetitions=[1, 1, 1]):
    '''Build a crystal from atomic positions, space group and cell
    parameters.
    
    **Parameters**

    positions: list of coordinates
        A list of the atomic positions 
    molecules: list of Molecule
        The molecules corresponding to the positions, the molecule will be
        translated in all the equivalent positions.
    group: int | str
        Space group given either as its number in International Tables
        or as its Hermann-Mauguin symbol.
    repetitions:
        Repetition of the unit cell in each direction
    cellpar:
        Unit cell parameters

    This function was taken and adapted from the *spacegroup* module 
    found in `ASE <https://wiki.fysik.dtu.dk/ase/>`_.

    The module *spacegroup* module was originally developed by Jesper
    Frills.

    '''
    sp = Spacegroup(group)
    sites, kind = sp.equivalent_sites(positions)

    nx, ny, nz = repetitions
    reptot = nx*ny*nz
    
    # Unit cell parameters
    a,b,c = cellpar_to_cell(cellpar)
    
    cry = System()
    i = 0
    with cry.batch() as batch:
        for x in range(nx):
            for y in range(ny):
                for z in range(nz):
                    for s, ki in zip(sites, kind):
                        tpl = molecules[ki]
                        tpl.move_to(s[0]*a +s[1]*b + s[2]*c + a*x + b*y + c*z)
                        batch.append(tpl.copy())

    # Computing the box_vectors
    cry.box_vectors = np.array([a*nx, b*ny, c*nz])
    
    return cry


# def crystal(symbols=None, basis=None, spacegroup=1, setting=1, 
#             cell=None, cellpar=None, 
#             ab_normal=(0,0,1), a_direction=None, size=(1,1,1),
#             ondublicates='warn', symprec=0.001, 
#             pbc=True, primitive_cell=False, **kwargs):
#     """Create a System instance for a conventional unit cell of a
#     space group.

#     Parameters:

#     symbols : str | sequence of str | sequence of Atom | Atoms
#         Element symbols of the unique sites.  Can either be a string
#         formula or a sequence of element symbols. E.g. ('Na', 'Cl')
#         and 'NaCl' are equivalent.  Can also be given as a sequence of
#         Atom objects or an Atoms object.
#     basis : list of scaled coordinates 
#         Positions of the unique sites corresponding to symbols given
#         either as scaled positions or through an atoms instance.  Not
#         needed if *symbols* is a sequence of Atom objects or an Atoms
#         object.
#     spacegroup : int | string | Spacegroup instance
#         Space group given either as its number in International Tables
#         or as its Hermann-Mauguin symbol.
#     setting : 1 | 2
#         Space group setting.
#     cell : 3x3 matrix
#         Unit cell vectors.
#     cellpar : [a, b, c, alpha, beta, gamma]
#         Cell parameters with angles in degree. Is not used when `cell`
#         is given. 
#     ab_normal : vector
#         Is used to define the orientation of the unit cell relative
#         to the Cartesian system when `cell` is not given. It is the
#         normal vector of the plane spanned by a and b.
#     a_direction : vector
#         Defines the orientation of the unit cell a vector. a will be 
#         parallel to the projection of `a_direction` onto the a-b plane.
#     size : 3 positive integers
#         How many times the conventional unit cell should be repeated
#         in each direction.
#     ondublicates : 'keep' | 'replace' | 'warn' | 'error'
#         Action if `basis` contain symmetry-equivalent positions:
#             'keep'    - ignore additional symmetry-equivalent positions
#             'replace' - replace
#             'warn'    - like 'keep', but issue an UserWarning
#             'error'   - raises a SpacegroupValueError
#     symprec : float
#         Minimum "distance" betweed two sites in scaled coordinates
#         before they are counted as the same site.
#     pbc : one or three bools
#         Periodic boundary conditions flags.  Examples: True,
#         False, 0, 1, (1, 1, 0), (True, False, False).  Default
#         is True.
#     primitive_cell : bool
#         Wheter to return the primitive instead of the conventional
#         unit cell.

#     Keyword arguments:

#     All additional keyword arguments are passed on to the Atoms
#     constructor.  Currently, probably the most useful additional
#     keyword arguments are `info`, `constraint` and `calculator`.

#     Examples:

#     Two diamond unit cells (space group number 227)

#     >>> diamond = crystal('C', [(0,0,0)], spacegroup=227, 
#     ...     cellpar=[3.57, 3.57, 3.57, 90, 90, 90], size=(2,1,1))
#     >>> ase.view(diamond)  # doctest: +SKIP

#     A CoSb3 skutterudite unit cell containing 32 atoms

#     >>> skutterudite = crystal(('Co', 'Sb'), 
#     ...     basis=[(0.25,0.25,0.25), (0.0, 0.335, 0.158)], 
#     ...     spacegroup=204, cellpar=[9.04, 9.04, 9.04, 90, 90, 90])
#     >>> len(skutterudite)
#     32
#     """
#     sg = Spacegroup(spacegroup, setting)
#     if (not isinstance(symbols, str) and 
#         hasattr(symbols, '__getitem__') and
#         len(symbols) > 0 and 
#         isinstance(symbols[0], ase.Atom)):
#         symbols = ase.Atoms(symbols)
#     if isinstance(symbols, ase.Atoms):
#         basis = symbols
#         symbols = basis.get_chemical_symbols()
#     if isinstance(basis, ase.Atoms):
#         basis_coords = basis.get_scaled_positions()
#         if cell is None and cellpar is None:
#             cell = basis.cell
#         if symbols is None:
#             symbols = basis.get_chemical_symbols()
#     else:
#         basis_coords = np.array(basis, dtype=float, copy=False, ndmin=2)
#     sites, kinds = sg.equivalent_sites(basis_coords, 
#                                        ondublicates=ondublicates, 
#                                        symprec=symprec)
#     symbols = parse_symbols(symbols)
#     symbols = [symbols[i] for i in kinds]
#     if cell is None:
#         cell = cellpar_to_cell(cellpar, ab_normal, a_direction)

#     info = dict(spacegroup=sg)
#     if primitive_cell:
#         info['unit_cell'] = 'primitive'
#     else:
#         info['unit_cell'] = 'conventional'

#     if 'info' in kwargs:
#         info.update(kwargs['info'])
#     kwargs['info'] = info

#     atoms = ase.Atoms(symbols, 
#                       scaled_positions=sites, 
#                       cell=cell,
#                       pbc=pbc,
#                       **kwargs)

#     if isinstance(basis, ase.Atoms):
#         for name in basis.arrays:
#             if not atoms.has(name):
#                 array = basis.get_array(name)
#                 atoms.new_array(name, [array[i] for i in kinds], 
#                                 dtype=array.dtype, shape=array.shape[1:])

#     if primitive_cell:
#         from ase.utils.geometry  import cut
#         prim_cell = sg.scaled_primitive_cell
#         atoms = cut(atoms, a=prim_cell[0], b=prim_cell[1], c=prim_cell[2])

#     if size != (1, 1, 1):
#         atoms = atoms.repeat(size)
#     return atoms

# def parse_symbols(symbols):
#     """Return `sumbols` as a sequence of element symbols."""
#     if isinstance(symbols, basestring):
#         symbols = string2symbols(symbols)
#     return symbols






#-----------------------------------------------------------------
# Self test
if __name__ == '__main__':
    import doctest
    #print 'doctest: ', doctest.testmod()
    
