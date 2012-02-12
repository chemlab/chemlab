"""Functional tests of chemlab, they show real life examples of the
usage of this package.

"""
import chemlab as cl

def bond_guessing_test():
    """Test if bonds are guessed properly."""
    mol = cl.readgeom("tests/data/sulphoxide.xyz",format="xyz")
    
    assert isinstance(mol, cl.Molecule)
    mol.guess_bonds()
    
    so_bond =  mol.get_bond(0, 1) # Not sure if getting a bond by
                                    # index tuple is a good idea

    assert so_bond, "The bond S-O doesn't exists"
    
    # Check if the bond order is 2, again, not sure if an order
    # attribute makes sense since we'll probably not support bond
    # orders like 2.5
    assert so_bond.order == 2

    sc_bond = mol.get_bond(1, 2)
    assert sc_bond
    assert sc_bond.order == 1
    
    ch_bond = mol.get_bond(2, 3)
    assert ch_bond
    assert ch_bond.order == 1

    # Verify if they at least correspond
    cc_benz_bond2 = mol.get_bond(8, 9)
    assert cc_benz_bond2
    assert cc_benz_bond2.order == 2
    
    cc_benz_bond1 = mol.get_bond(7, 8)
    assert cc_benz_bond1
    assert cc_benz_bond1.order == 1


def gamess_parser_test():
    """Test the parsing of a gamess data file."""
    
    # Read a gamess datafile containing a saddle point optimization
    dfile = cl.read_datafile("tests/data/1-so.out", "gamout")
    
    # Grab the last point and check the types
    last = dfile["irc"]["geometries"][-1]
    assert isinstance(last, cl.Molecule)
