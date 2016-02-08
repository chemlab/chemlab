from .base import ChemicalEntity
from .attributes import Field

class Atom(ChemicalEntity):
    __dimension__ = 'atom'
    __fields__ = {
        'r_array' : Field(alias='r', shape=(3,), dtype='float'),
        'type_array' : Field(dtype='U4', alias='type'),
        'charge_array' : Field(dtype='float', alias='charge'),
        'atom_export' : Field(dtype=object, alias='export'),
        'atom_name' : Field(dtype='unicode', alias='name')
    }

    def __init__(self, type, r_array, name=None, export=None):
        super(Atom, self).__init__()
        self.r_array = r_array
        self.type_array = type
        if name:
            self.atom_name = name
        self.export = export or {}
    
    @classmethod
    def from_fields(cls, **kwargs):
        '''
        Create an `Atom` instance from a set of fields. This is a
        slightly faster way to initialize an Atom.
        
        **Example**

        >>> Atom.from_fields(type='Ar',
                             r_array=np.array([0.0, 0.0, 0.0]),
                             mass=39.948,
                             export={})
        '''
        obj = cls.__new__(cls)
        
        for name, field in obj.__fields__.items():
            if name in kwargs:
                field.value = kwargs[name]
        
        return obj
