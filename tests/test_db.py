from chemlab.db import CirDB
from chemlab.db import LocalDB
from chemlab.db import ChemSpiderDB
from chemlab.db import RcsbDB
from chemlab.db import ChemlabDB
from chemlab.db.base import EntryNotFound

from chemlab.core import System

from nose.tools import assert_raises
from nose.plugins.attrib import attr

from .testtools import npeq_

@attr('slow')
def test_cir():
    db = CirDB()
    bz = db.get("molecule", "norbornene")

def test_local():
    db = ChemlabDB()
    bz = db.get("molecule", "example.norbornene")
    pre_dict = bz.to_dict()

    db = LocalDB("/tmp/testdb/")
    db.store("molecule", 'norbornene', bz, nowarn=True)
    
    post_dict = db.get('molecule', 'norbornene').to_dict()
    
    npeq_(pre_dict['r_array'], post_dict['r_array'])
    
    # Do the same thing for a system of 3 norbornenes
    s = System([bz.copy() for i in range(3)])
    pre_dict = s.to_dict()
    db.store("system", 'norbornene-3', s, nowarn=True)
    post_dict = db.get('system', 'norbornene-3').to_dict()
    
    npeq_(pre_dict['r_array'], post_dict['r_array'])
    
    
def test_rcsb():
    db = RcsbDB()
    
    # Test for failure
    #with assert_raises(EntryNotFound):
    #    mol = db.get('molecule', 'nonexistent')
        
    mol = db.get('molecule', '3ZJE')
    assert mol.n_atoms == 5697
    
def test_chemspider():
    
    try:
        db = ChemSpiderDB()
    except:
        return
    
    name = 'fullerene'
    mol = db.get('molecule', name)
    print((db.get('inchi', name)))
    print((db.get('molecularformula', name)))
    print((db.get('imageurl', name)))
    print((db.get('smiles', name)))
    print((db.get('averagemass', name)))
    print((db.get('nominalmass', name)))
    print((db.get('molecularweight', name)))
    print((db.get('inchikey', name)))
    print((db.get('molecularformula', name)))
    print((db.get('alogp', name)))
    print((db.get('xlogp', name)))
    print((db.get('image', name)))
    print((db.get('mol2d', name)))
    print((db.get('commonname', name)))

# TODO: toxnet is not working at all
# @attr('slow')
# def test_toxnet():
#     from chemlab.db.toxnetdb import ToxNetDB
#     
#     db = ToxNetDB()
#     testcompounds = ['methane', 'ethane', 'propane', 'butane',
#                      'sodium chloride']
#     for c in testcompounds:
#         print(('Melting point', c, db.get('melting point', c)))
#         print(('Boiling point', c, db.get('boiling point', c)))

    
    #db.get('boiling point', 'merda')
