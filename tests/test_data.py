from chemlab.data.cirdb import CirDB
from chemlab.graphics import display_molecule

def test_cir():
    db = CirDB()
    bz = db.get("norbornene", "molecule")
    display_molecule(bz)
