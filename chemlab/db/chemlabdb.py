from .base import AbstractDB
from .local import LocalDB
import os

class ChemlabDB(AbstractDB):
    """Chemlab default database.
    
    It contains some pretty generic atomic data and some example
    molecules and systems.

    """

    def __init__(self):
        curdir = os.path.dirname(__file__) + '/localdb'
        self.directory = curdir
        self.ldb = LocalDB(curdir)
        
    def get(self, feature, key, *args, **kwargs):
        if feature in ('molecule', 'system'):
            return self.ldb.get(feature, key)
        
        if feature == 'data':
            fd = open(os.path.join(self.directory,
                                   "data", "element.txt"))

            lines = fd.readlines()
            lines = [l for l in lines if not l.startswith('#')]
            fields = [l.split() for l in lines]

            if key == 'vdwdict':
                vdw_tuples = [(f[1], float(f[5])/10) for f in fields]
                vdw_dict = dict(vdw_tuples)
                fd.close()
                return vdw_dict
            if key == 'massdict':
                mass_tuples = [(f[1], float(f[5])/10) for f in fields]
                mass_dict = dict(mass_tuples)
                fd.close()
                return mass_dict

            if key == 'symbols':
                return [f[1] for f in fields]
