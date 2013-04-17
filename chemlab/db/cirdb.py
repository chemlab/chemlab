'''CIR database

'''
from .base import EntryNotFound, AbstractDB
from ..libs import cirpy
from StringIO import StringIO
from ..io.handlers import MolIO


class CirDB(AbstractDB):
    def get(self, feature, key):
        if feature == "molecule":
            result = cirpy.resolve(key, "sdf", get3d=True)
            if result:
                fd = StringIO(result)
                return MolIO(fd).read("molecule")
                
            else:
                raise EntryNotFound()
        else:
            raise Exception("feature not present")