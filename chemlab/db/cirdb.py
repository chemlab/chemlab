'''CIR database

'''
from .base import EntryNotFound, AbstractDB
from ..libs import cirpy

from io import BytesIO

class CirDB(AbstractDB):
    """Get 3D structure of arbitrary molecules given a string
    identifier.
    
    .. method:: get(self, 'molecule', key)

      Retrieve a molecule from the online `CIR
      <http://cactus.nci.nih.gov/chemical/structure>`_ database by
      passing an identifier.
    
      A *key* can be, for instance, the common name of a certain
      chemical, a SMILES string or an InChi identifier. This is just
      an adapter on the `CirPy <https://github.com/mcs07/CIRpy>`_ library.
    
      Returns a Molecule instance.

    """

    def get(self, feature, key):
        from ..io.handlers import MolIO
        
        if feature == "molecule":
            result = cirpy.resolve(key, "sdf", get3d=True)
            if result:
                fd = BytesIO(result.encode('utf-8'))
                return MolIO(fd).read("molecule")
                
            else:
                raise EntryNotFound()
        else:
            raise Exception("feature not present")