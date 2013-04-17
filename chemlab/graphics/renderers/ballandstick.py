from .base import AbstractRenderer
from .atom import AtomRenderer
from .bond import BondRenderer

from ...data import cdb

vdw_dict = cdb.get("vdwdict", "data")

class BallAndStickRenderer(AbstractRenderer):
    def __init__(self, widget, r_array, type_array, bonds):
        super(BallAndStickRenderer, self).__init__(widget)
        
        scale = 0.3
        for k in vdw_dict:
            vdw_dict[k] = vdw_dict[k] * scale
        
        self.ar = AtomRenderer(widget, r_array, type_array, radii_map = vdw_dict)
        self.br = BondRenderer(widget, bonds, r_array, type_array)
        
    def draw(self):
        self.ar.draw()
        self.br.draw()

    def update_positions(self, r_array):
        self.ar.update_positions(r_array)
        self.br.update_positions(r_array)