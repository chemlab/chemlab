"""Contains all the functions to display atoms, bonds etc..."""
from shapes import sphere, cylinder
import colors

def draw_molecule(molecule):
    
    for atom in molecule.atoms:
        color = colors.map.get(atom.type, colors.light_grey)
        sphere(atom.coords, 0.4, color)

    for bond in molecule.bonds:
        cylinder(bond.start.coords, bond.end.coords, 0.1)

from ..gletools.shapes import Sphere, Cylinder

def draw_molecule2(molecule):
    for atom in molecule.atoms:
        color = colors.map.get(atom.type, colors.light_grey)
        s = Sphere(0.4, atom.coords, color)
        s.draw()
        
        
    for bond in molecule.bonds:
        c = Cylinder(0.1, bond.start.coords, bond.end.coords)
        s.draw()

        
    

