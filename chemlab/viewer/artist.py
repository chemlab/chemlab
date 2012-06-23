"""Contains all the functions to display atoms, bonds etc..."""
from shapes import sphere, cylinder
import colors

def draw_molecule(molecule):
    
    for atom in molecule.atoms:
        color = colors.map.get(atom.type, colors.light_grey)
        sphere(atom.coords, 0.4, color)

    for bond in molecule.bonds:
        cylinder(bond.start.coords, bond.end.coords, 0.1)

    