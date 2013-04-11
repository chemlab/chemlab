'''CIR database

'''
from ..libs import cirpy
from StringIO import StringIO
from ..io.handlers import MolIO

class EntryNotFound(Exception):
    pass

class CirDB(object):
    def get(self, identifier, feature):
        if feature == "molecule":
            result = cirpy.resolve(identifier, "sdf", get3d=True)
            if result:
                fd = StringIO(result)
                return MolIO(fd).read("molecule")
                
            else:
                raise EntryNotFound()
        else:
            raise Exception("feature not present")