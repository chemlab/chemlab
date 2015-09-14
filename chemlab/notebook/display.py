import numpy as np
from ..graphics import Scene
from chemview.render import render_povray

class Display(object):
    
    def __init__(self, backend, radiosity=False):
        self.backend = backend
        
        self.settings = { 'radiosity' : radiosity }
        
        if backend == 'povray':
            self.plotter = Plotter3D()
        else:
            raise NotImplementedError()

    def system(self, object, highlight=None, alpha=1.0, color=None, 
                     transparent=None):
        '''Display System object'''
        if self.backend == 'povray':
            kwargs = {}
            if color is not None:
                kwargs['color'] = color
            else:
                kwargs['color'] = default_colormap[object.type_array]
            
            self.plotter.camera.autozoom(object.r_array)
            self.plotter.points(object.r_array, alpha=alpha, **kwargs)
            return self

    def render(self):
        if self.backend == 'povray':
            return render_povray(self.plotter.to_dict(), extra_opts=self.settings)

    
def expand_scalar_or_list(value, size, dtype=None, msg=''):
    if isinstance(value, (float, int)):
        ret = np.repeat(value, size)
    elif isinstance(value, (list, np.ndarray)):
        ret = np.asarray(value, dtype=dtype)
    else:
        raise ValueError(msg)
    return ret.astype(dtype)

class VectorizedMap(object):
    
    def __init__(self, map, default=None, ignorecase=False):
        
        if ignorecase:
            self.map = { k.lower(): v for k, v in map.items() }
        else:
            self.map = map
        
        self.ignorecase = ignorecase

    def __getitem__(self, names):
        if isinstance(names, (list, np.ndarray)):
            if self.ignorecase:
                return [self.map[n.lower()] for n in names]
            else:
                return [self.map[n] for n in names]
        else:
            if self.ignorecase:
                n = n.lower()
            return self.map[names]

    def __repr__(self):
        return repr(self.map)

atomColors = {
    "H": 0xFFFFFF,
    "HE": 0xD9FFFF,
    "LI": 0xCC80FF,
    "BE": 0xC2FF00,
    "B": 0xFFB5B5,
    "C": 0x909090,
    "N": 0x3050F8,
    "O": 0xFF0D0D,
    "F": 0x90E050,
    "NE": 0xB3E3F5,
    "NA": 0xAB5CF2,
    "MG": 0x8AFF00,
    "AL": 0xBFA6A6,
    "SI": 0xF0C8A0,
    "P": 0xFF8000,
    "S": 0xFFFF30,
    "CL": 0x1FF01F,
    "AR": 0x80D1E3,
    "K": 0x8F40D4,
    "CA": 0x3DFF00,
    "SC": 0xE6E6E6,
    "TI": 0xBFC2C7,
    "V": 0xA6A6AB,
    "CR": 0x8A99C7,
    "MN": 0x9C7AC7,
    "FE": 0xE06633,
    "CO": 0xF090A0,
    "NI": 0x50D050,
    "CU": 0xC88033,
    "ZN": 0x7D80B0,
    "GA": 0xC28F8F,
    "GE": 0x668F8F,
    "AS": 0xBD80E3,
    "SE": 0xFFA100,
    "BR": 0xA62929,
    "KR": 0x5CB8D1,
    "RB": 0x702EB0,
    "SR": 0x00FF00,
    "Y": 0x94FFFF,
    "ZR": 0x94E0E0,
    "NB": 0x73C2C9,
    "MO": 0x54B5B5,
    "TC": 0x3B9E9E,
    "RU": 0x248F8F,
    "RH": 0x0A7D8C,
    "PD": 0x006985,
    "AG": 0xC0C0C0,
    "CD": 0xFFD98F,
    "IN": 0xA67573,
    "SN": 0x668080,
    "SB": 0x9E63B5,
    "TE": 0xD47A00,
    "I": 0x940094,
    "XE": 0x429EB0,
    "CS": 0x57178F,
    "BA": 0x00C900,
    "LA": 0x70D4FF,
    "CE": 0xFFFFC7,
    "PR": 0xD9FFC7,
    "ND": 0xC7FFC7,
    "PM": 0xA3FFC7,
    "SM": 0x8FFFC7,
    "EU": 0x61FFC7,
    "GD": 0x45FFC7,
    "TB": 0x30FFC7,
    "DY": 0x1FFFC7,
    "HO": 0x00FF9C,
    "ER": 0x00E675,
    "TM": 0x00D452,
    "YB": 0x00BF38,
    "LU": 0x00AB24,
    "HF": 0x4DC2FF,
    "TA": 0x4DA6FF,
    "W": 0x2194D6,
    "RE": 0x267DAB,
    "OS": 0x266696,
    "IR": 0x175487,
    "PT": 0xD0D0E0,
    "AU": 0xFFD123,
    "HG": 0xB8B8D0,
    "TL": 0xA6544D,
    "PB": 0x575961,
    "BI": 0x9E4FB5,
    "PO": 0xAB5C00,
    "AT": 0x754F45,
    "RN": 0x428296,
    "FR": 0x420066,
    "RA": 0x007D00,
    "AC": 0x70ABFA,
    "TH": 0x00BAFF,
    "PA": 0x00A1FF,
    "U": 0x008FFF,
    "NP": 0x0080FF,
    "PU": 0x006BFF,
    "AM": 0x545CF2,
    "CM": 0x785CE3,
    "BK": 0x8A4FE3,
    "CF": 0xA136D4,
    "ES": 0xB31FD4,
    "FM": 0xB31FBA,
}

default_colormap = VectorizedMap(atomColors, 
                                 ignorecase=True,
                                 default=0xffffff)

class Plotter3D(Scene):
    
    def points(self, coordinates, size=1.0, color=0xffffff, alpha=1.0):
        coordinates = np.asarray(coordinates, dtype='float32')
        sizes = expand_scalar_or_list(size,
                                      len(coordinates), 
                                      dtype='float', 
                                      msg='sizes can be either number or list')
        alpha = expand_scalar_or_list(alpha,
                                      len(coordinates), 
                                      dtype='float', 
                                      msg='alpha can be either number or list')
        
        colors = expand_scalar_or_list(color,
                                       len(coordinates), 
                                       dtype='int', 
                                       msg='colors can be either integer or list')
        
        self.add_representation('points', {'coordinates': coordinates,
                                           'colors': colors,
                                           'sizes': sizes,
                                           'alpha' : alpha
                                           })
    def render(self):
        render_povray(self.to_dict())
    
