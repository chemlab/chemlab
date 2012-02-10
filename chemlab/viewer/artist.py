"""Contains all the functions to display atoms, bonds etc..."""
from shapes import sphere, cylinder

def draw_molecule(molecule):
    for atom in molecule.atoms:
        sphere(atom.coords, 0.4)

    for bond in molecule.bonds:
        cylinder(bond.start.coords, bond.end.coords, 0.1)