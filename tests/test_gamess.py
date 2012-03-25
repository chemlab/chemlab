from chemlab.dataparsers.gamess import GamessDataParser
from chemlab import read_datafile
from chemlab import Molecule
from chemlab.viewer import display

def test_irc():
    """Test if irc parsing works correctly."""

    gms = GamessDataParser("tests/data/1-so.out")
    
    assert gms.get_avail_properties() == set(["irc"])
    
    geoms = gms.get_property("irc")["geometries"]
    assert isinstance(geoms, list)
    first = geoms[0]
    assert isinstance(first, Molecule)

def test_exc():
    """Test if excited state parsing works."""

    gms = read_datafile("tests/data/1-so-sing.out", "gamout")

    assert gms.properties == set(["energy"])
    assert len(gms["energy"]["states"]) == 4
