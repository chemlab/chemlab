'''Hidden module to abstract the cclib interface and convert it to chemlab

'''
from .base import FormatNotSupported, IOHandler
from ...core import Molecule
from ...db import ChemlabDB
import numpy as np

import logging

from cclib.parser import (ADF,
                          GAMESS, 
                          GAMESSUK, Gaussian, Jaguar, Molpro, 
                          #NWChem, 
                          ORCA, 
                          # Psi, 
                          #QChem
                          )
_types = { 'gamess' : GAMESS,
           'gamessuk': GAMESSUK, 
           'gaussian': Gaussian, 
           'jaguar': Jaguar, 
           'molpro': Molpro, 
           #'nwchem': NWChem, 
           'orca': ORCA
         }

cdb = ChemlabDB()
symbols = cdb.get('data', 'symbols')

def _create_cclib_handler(type):
    if type not in _types:
        raise FormatNotSupported(type)

    class _Handler(IOHandler):

        def __init__(self, fd, filetype=type):
            super(_Handler, self).__init__(fd)
            self.filetype = filetype
            self.data = _types[filetype](fd, loglevel=logging.ERROR).parse()

        def read(self, feature, *args):
            if feature == 'molecular orbitals':
                n = args[0]
                basis_functions = self.data.gbasis
            if feature == 'molecule':
                # Angstrom to nanometers
                return Molecule.from_arrays(r_array=self.data.atomcoords[0]/10, 
                                            type_array=np.array([symbols[a] for a in self.data.atomnos]))
            else:
                return getattr(self.data, feature)

        def available_features(self):
            return set(self.data._attrlist) & set(dir(self.data))

    # Setting consistent class Name
    _Handler.__name__ = _types[type].__name__ + 'Handler'

    return _Handler

_cclib_handlers = [(_create_cclib_handler(format), format) for format in _types]
