from chemlab.db.cirdb import CirDB
from chemlab.db.local import LocalDB
from chemlab.graphics import display_molecule

def test_cir():
    db = CirDB()
    bz = db.get("norbornene", "molecule")
    display_molecule(bz)

def test_local():
    db = LocalDB("chemlab/data/localdb")
    water = db.get("gromacs.spce", "molecule")
    li = db.get("gromacs.li+", "molecule")
    cl = db.get("gromacs.cl-", "molecule")
    