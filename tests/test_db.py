from chemlab.db.cirdb import CirDB
from chemlab.db.local import LocalDB
from chemlab.db.chemspiderdb import ChemSpiderDB
from chemlab.graphics import display_molecule
from chemlab.core import System

from nose.tools import assert_raises
def test_cir():
    db = CirDB()
    bz = db.get("molecule", "norbornene")

def test_local():
    # Fetch some stuff from cirdb
    db = CirDB()
    bz = db.get("molecule", "norbornene")

    pre_string = bz.tojson()
    db = LocalDB("/tmp/testdb/")
    db.store("molecule", 'norbornene', bz, nowarn=True)
    
    post_string = db.get('molecule', 'norbornene').tojson()
    assert pre_string == post_string
    
    # Do the same thing for a system of 3 norbornenes
    s = System([bz.copy() for i in range(3)])
    pre_string = s.tojson()
    db.store("system", 'norbornene-3', s, nowarn=True)
    post_string = db.get('system', 'norbornene-3').tojson()
    
    assert pre_string == post_string
    
def test_chemspider():
    
    try:
        db = ChemSpiderDB()
    except:
        return
    
    name = 'fullerene'
    mol = db.get('molecule', name)
    print db.get('inchi', name)
    print db.get('molecularformula', name)
    print db.get('imageurl', name)
    print db.get('smiles', name)
    print db.get('averagemass', name)
    print db.get('nominalmass', name)
    print db.get('molecularweight', name)
    print db.get('inchikey', name)
    print db.get('molecularformula', name)
    print db.get('alogp', name)
    print db.get('xlogp', name)
    print db.get('image', name)
    print db.get('mol2d', name)
    print db.get('commonname', name)

def test_toxnet():
    from chemlab.db.toxnetdb import ToxNetDB
    
    db = ToxNetDB()
    testcompounds = ['methane', 'ethane', 'propane', 'butane',
                     'sodium chloride']
    for c in testcompounds:
        print 'Melting point', c, db.get('melting point', c)
        print 'Boiling point', c, db.get('boiling point', c)

    
    #db.get('boiling point', 'merda')