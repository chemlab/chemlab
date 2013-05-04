'''ChemSpider database
'''
from .base import EntryNotFound, AbstractDB
from ..libs import chemspipy
from StringIO import StringIO

class ChemSpiderDB(AbstractDB):
    """Get 3D structure of arbitrary molecules given a string
    identifier.
    
    .. method:: get(self, 'molecule', key)

      Retrieve a molecule from the online `Chemspider`_ database by
      passing an identifier.
    
      A *key* can be, for instance, the common name of a certain
      chemical, a SMILES string or an InChi identifier. This is just
      an adapter on the `chemspipy
      <https://github.com/mcs07/chemspipy>`_ library.
    
      Returns a Molecule instance.

    """
    def __init__(self, token=None):
        if not token:
            raise Exception('Need to pass the chemspider token.')
        else:
            # I know, this is monkeypatching but it should do the
            # trick.
            chemspipy.TOKEN = token
    
    def get(self, feature, key):
        from ..io.handlers import MolIO
        
        if feature == "molecule":
            result = chemspipy.find_one(key)
            
            if result:
                sdf = result.mol3d
                fd = StringIO(sdf)
                return MolIO(fd).read("molecule")
                
            else:
                raise EntryNotFound()
        else:
            raise Exception("feature not present")