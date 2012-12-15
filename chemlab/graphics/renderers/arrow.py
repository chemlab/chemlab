class ArrowRenderer(AbstractRenderer):
    def __init__(self, forces, atoms):
        self.set_forces(forces, atoms)
        
    def set_forces(self, forces, atoms):
        self.forces = forces
        self.atoms = atoms
        
    def draw(self):
        for f, a in zip(self.forces, self.atoms):
            arr = Arrow(f + a.coords, a.coords)
            arr.draw()

