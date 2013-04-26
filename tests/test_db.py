from chemlab.db.cirdb import CirDB
from chemlab.db.local import LocalDB
from chemlab.graphics import display_molecule
from chemlab.core import System

def test_cir():
    db = CirDB()
    bz = db.get("molecule", "norbornene")
    display_molecule(bz)

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