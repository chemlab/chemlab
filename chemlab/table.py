'''Periodic table data'''
import numpy as np

from .db import ChemlabDB

db = ChemlabDB()

_symbols = db.get('data', 'symbols')
_weight = db.get('data', 'massdict')
_vdw = db.get('data', 'vdwdict')

def atomic_no(atom):
    if isinstance(atom, (list, np.ndarray)):
        return np.array([atomic_no(a) for a in atom])
    else:
        return _symbols.index(atom)

def atomic_weight(atom):
    if isinstance(atom, (list, np.ndarray)):
        return np.array([atomic_weight(a) for a in atom])
    else:
        return _weight[atom]

def vdw_radius(atom):
    if isinstance(atom, (list, np.ndarray)):
        return np.array([vdw_radius(a) for a in atom])
    else:
        return _vdw[atom]
