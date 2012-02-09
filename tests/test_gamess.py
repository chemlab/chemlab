from chemlab.dataparsers.gamess import GamessDataParser
from chemlab import Molecule

def test_parse():
    gms = GamessDataParser("tests/data/1-so.out")
    assert gms.avail_props() == set("irc")
    geoms = gms.get_property("irc")["geometries"]
    assert isinstance(geoms, list)
    first = geoms[0]
    assert isinstance(first, Molecule)
