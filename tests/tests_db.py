from chemlab.db.cirdb import CirDB
from chemlab.db.local import LocalDB
from chemlab.graphics import display_molecule

def test_cir():
    db = CirDB()
    bz = db.get("molecule", "norbornene")
    display_molecule(bz)

def test_local():
    db = LocalDB("chemlab/data/localdb")
    water = db.get("molecule", "gromacs.spce")
    li = db.get("molecule", "gromacs.li+")
    cl = db.get("molecule", "gromacs.cl-")
