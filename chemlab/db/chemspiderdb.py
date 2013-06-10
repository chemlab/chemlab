'''ChemSpider database
'''
import os
import sys
from io import BytesIO

from .base import EntryNotFound, AbstractDB
from ..libs import chemspipy
try:
    import configparser
except:
    import ConfigParser as configparser


class ChemSpiderDB(AbstractDB):
    """Retrieve data from the online `Chemspider
      <http://www.chemspider.com>`_ database by passing an string identifier.

      **Parameters**

      token: str | None
          The chemspider security token. When token is None, chemlab will
          try to retrieve the token from a configuration file in $HOME/.chemlabrc
          that has the entry::
            
            [chemspider]
            token=YOUR-SECURITY-TOKEN
          
      
      The *get* method requires a *key* argument to retrieve a database
      entry. A valid *key* can be, for instance, the common name of a
      certain chemical, a SMILES string or an InChi identifier. This
      is just an adapter on the `chemspipy
      <https://github.com/mcs07/chemspipy>`_ library.
    
      .. method:: get(self, 'molecule', key)
      
         Retrieve a molecule 3D structure.
         Returns a :class:`~chemlab.core.Molecule` instance.
      
      .. method:: get(self, 'inchi', key)
      
         Retrieve the InChi string for the compound.
      
      .. method:: get(self, 'molecularformula', key)
         
         Retrieve the molecular formula as a LaTeX string.
      
      .. method:: get(self, 'imageurl', key)
      
          Retrieve the url of a 2D image representation of the compound.
      
      .. method:: get(self, 'smiles', key)
      
          Retrieve the SMILES string for the compound.
      
      .. method:: get(self, 'averagemass', key)
      
          Retrieve the average mass
      
      .. method:: get(self, 'nominalmass', key)
      
          Retrieve the nominal mass
      
      .. method:: get(self, 'inchikey', key)
      
          Return the InChi key.
      
      .. method:: get(self, 'alogp', key)
      
          Predicted LogP (partition coefficient) using the ACD LogP algorithm.
      
      .. method:: get(self, 'xlogp', key)
      
          Predicted LogP using the XLogP algorithm.
      
      .. method:: get(self, 'image', key)
      
          PNG image of the compound as a data string.
      
      .. method:: get(self, 'mol2d', key)
      
          MOL mdl file containing 2D coordinates of the compound.
      
      .. method:: get(self, 'commonname', key)
      
          Retrieve the common name of the compound.

    """
    def __init__(self, token=None):
        if not token:
            config = configparser.ConfigParser()
            userconfig = os.path.expanduser('~/.chemlabrc')
            
            config.read([userconfig])
            try:
                token = config.get('chemspider', 'token')
                chemspipy.TOKEN = token
            except configparser.NoSectionError:
                lines = ('',
                         '-'*70,
                         'You need to write your chemspider token in order to use the database.',
                         'Register on http://www.chemspider.com and either',
                         'pass the security token as an argument to the ChemSpiderDB constructor',
                         'or write the security token in the',
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
            
            fd = BytesIO(sdf.encode('utf-8'))
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