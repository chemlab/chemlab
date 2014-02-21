from .base import IOHandler
from .utils import guess_type

import re


class CifIO(IOHandler):
    can_read = ['fract', 'cellpar', 'group']
    
    def __init__(self, *a, **kw):
        super(CifIO,self).__init__(*a, **kw)
        self.text = self.fd.read()

    
    def read(self, feature):
        super(CifIO,self).read(feature)

        text = self.text
        a = float(re.findall("_cell_length_a\s+(.*)", text)[0])/10
        b = float(re.findall("_cell_length_b\s+(.*)", text)[0])/10
        c = float(re.findall("_cell_length_c\s+(.*)", text)[0])/10
        
        alpha = float(re.findall("_cell_angle_alpha\s+(.*)", text)[0])
        beta = float(re.findall("_cell_angle_beta\s+(.*)", text)[0])
        gamma = float(re.findall("_cell_angle_gamma\s+(.*)", text)[0])

        group = re.findall("_symmetry_space_group_name_H-M\s+'(.*?)'", text)[0]

        # Fractional coordinates
        lines = text.splitlines()
        
        fract = []
        start = False
        for i, l in enumerate(lines):
            if start:
                if 'loop_' in l:
                    break
                fract.append(l)

            if '_atom_site_fract_z' in l:
                start = True

        res = []
        for f in fract:
            tp, x, y, z = f.split()
            # Massaging
            tp = guess_type(tp)
            x = float(x)
            y = float(y)
            z = float(z)
            res.append((tp, x, y, z))
            
        if feature == 'fract':
            return res

        if feature == 'cellpar':
            return [a, b, c, alpha, beta, gamma]
        
        if feature == 'group':
            return group