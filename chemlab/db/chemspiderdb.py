'''ChemSpider database
'''
from .base import EntryNotFound, AbstractDB
from ..libs import chemspipy
from StringIO import StringIO
import ConfigParser, os
import sys

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
            config = ConfigParser.ConfigParser()
            userconfig = os.path.expanduser('~/.chemlabrc')
            
            config.read([userconfig])
            try:
                token = config.get('chemspider', 'token')
                chemspipy.TOKEN = token
            except ConfigParser.NoSectionError:
                lines = ('',
                         '-'*70,
                         'You need to write your chemspider token in order to use the database.',
                         'Register on http://www.chemspider.com and write the security token in the',
                         '%s file in this way:'%userconfig,
                         '',
                         '# file .chemlabrc',
                         '[chemspider]',
                         'token=YOUR-SECURITY-TOKEN',
                         '',
                         '-'*70)
                raise Exception('\n'.join(lines))
        else:
            # I know, this is monkeypatching but it should do the
            # trick.
            chemspipy.TOKEN = token
    
    def get(self, feature, key):
        from ..io.handlers import MolIO
        result = chemspipy.find_one(key)
        if not result:
            raise EntryNotFound()
        
        if feature == "molecule":
            sdf = result.mol3d
            fd = StringIO(sdf)
            return MolIO(fd).read("molecule")
        elif feature == 'inchi':
            return result.inchi
        elif feature == 'imageurl':
            return result.imageurl
        elif feature == 'smiles':
            return result.smiles
        elif feature == 'averagemass':
            return result.averagemass
        elif feature == 'nominalmass':
            return result.nominalmass
        elif feature == 'molecularweight':
            return result.molecularweight
        elif feature == 'inchikey':
            return result.inchikey
        elif feature == 'molecularformula':
            return result.mf
        elif feature == 'alogp':
            return result.alogp
        elif feature == 'xlogp':
            return result.xlogp
        elif feature == 'image':
            return result.image
        elif feature == 'mol2d':
            return result.mol
        elif feature == 'commonname':
            return result.commonname
        else:
            raise Exception("%s feature not present"%feature)