from .base import AbstractDB
from .local import LocalDB
import os

class ChemlabDB(AbstractDB):
    """Chemlab default database.
    
    This database contains some example molecules and some atomic
    data.
    
    .. method:: get(self, 'molecule', key)
    
        Retrieve a molecule from the database.
        The included molecule keys are:

        - example.water
        - example.norbornene
        - gromacs.spc
        - gromacs.spce
        - gromacs.na+
        - gromacs.cl-

    .. method:: get(self, 'data', key)
    
        Retrieve atomic data. The available data is:

        - vdwdict: Dictionary with per-element Van Der Waals radii.
        - massdict: Dictionary of masses.
        - symbols: Atomic symbols in a list.

        Data was taken from the `OpenBabel <http://openbabel.org>`_ distribution.
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
                mass_tuples = [(f[1], float(f[7])) for f in fields]
                mass_dict = dict(mass_tuples)
                fd.close()
                return mass_dict

            if key == 'covalentdict':
                covalent_tuples = [(f[1], float(f[3])/10) for f in fields]
                covalent_dict = dict(covalent_tuples)
                fd.close()
                return covalent_dict
                
            if key == 'symbols':
                return [f[1] for f in fields]
