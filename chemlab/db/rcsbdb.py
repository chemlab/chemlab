from io import BytesIO

from .base import AbstractDB, EntryNotFound


# Python 2-3 compatibility
try:
    from urllib.parse import quote_plus
    from urllib.request import urlopen
except ImportError:
    from urllib import quote_plus
    from urllib2 import urlopen


class RcsbDB(AbstractDB):
    """Access to the `RCSB <http://www.rcsb.org/>`_ database for
    proteins.

    To download a protein, just write its PDB id that you can check
    on the website::

        from chemlab.db import RcsbDB
        mol = RcsbDB().get('molecule', '3ZJE')

    .. method:: get(self, 'molecule', key)
        
        The 4 alphanumeric PDB entry that you can get from the
        `RCSB <http://www.rcsb.org/>`_ website.

    """

    def get(self, feature, key):
        from ..io.handlers import PdbIO # Here to avoid circular import
        
        if feature == 'molecule':
            url = 'http://www.rcsb.org/pdb/files/%s.pdb' % key
            result = urlopen(url)
            pdbtext = result.read()
            if pdbtext.startswith(b'<!DOCTYPE'):
                raise EntryNotFound()
            
            fd = BytesIO(pdbtext)
            
            return PdbIO(fd).read('molecule')
            
        else:
            raise Exception('Feature {} not supported'.format(feature))
